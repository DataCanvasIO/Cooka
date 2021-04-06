# -*- encoding: utf-8 -*-
from os import path as P

from tornado import gen

from cooka.common import util
from cooka.common.consts import CODE_NOT_FILE
from cooka.common.exceptions import IllegalParamException, EntityNotExistsException
from cooka.common.exceptions import ServiceException
from cooka.common.model import SampleConf, AnalyzeStep, JobStep
from cooka.dao import db
from cooka.dao.entity import MessageEntity, DatasetEntity
from cooka.handler.base_handler import BaseHandler
from cooka.common.model import Feature
from cooka.service.dataset_service import DatasetService
from cooka.service.experiment_service import ExperimentService
from cooka.common import consts
from cooka.common.authentication import authenticated


class DatasetHandler(BaseHandler):

    dataset_service = DatasetService()

    @gen.coroutine
    @authenticated
    def post(self, *args, **kwargs):
        # 1. validate param
        request_body = self.get_request_as_dict_if_json()
        print("request_body:")
        print(request_body)
        dataset_name = util.require_in_dict(request_body, 'dataset_name', str)
        temporary_dataset_name = util.require_in_dict(request_body, 'temporary_dataset_name', str)

        # 2. create
        self.dataset_service.create_dataset(dataset_name, temporary_dataset_name)

        self.response_json({})

    @gen.coroutine
    @authenticated
    def get(self, *args, **kwargs):
        args = self.get_query_args()
        datasets, count = self.dataset_service.brevity_dataset_pagination(req_dict=args)
        self.response_json({"datasets": datasets, "count": count})

    @gen.coroutine
    @authenticated
    def delete(self, dataset_name, *args, **kwargs):
        # 1. validate param
        if dataset_name is None:
            raise IllegalParamException("dataset_name", None, "not empty")

        path_dataset = P.join(consts.PATH_DATASET, dataset_name)
        if not P.exists(path_dataset):
            raise EntityNotExistsException(EntityNotExistsException.Entities.Dataset, dataset_name)

        meta_file = P.join(path_dataset, 'meta.json')
        if not P.exists(meta_file):
            raise ValueError(f"Dataset={dataset_name} is broken.")

        with open(meta_file, 'r') as f:
            meta_dict = util.loads(f.read())

        self.response_json(meta_dict)


class DatasetItemHandler(BaseHandler):
    dataset_service = DatasetService()

    @gen.coroutine
    @authenticated
    def get(self, dataset_name, *args, **kwargs):

        query_args = self.get_query_args()

        n_top_value = util.require_in_dict(query_args, 'n_top_value', int, 10)

        d = self.dataset_service.retrieve(dataset_name, n_top_value)

        self.response_json(d)

    @gen.coroutine
    @authenticated
    def delete(self, dataset_name, *args, **kwargs):
        self.dataset_service.delete(dataset_name)
        self.response_json({})


class DatasetNameHandler(BaseHandler):

    dataset_service = DatasetService()

    @gen.coroutine
    @authenticated
    def post(self, dataset_name, *args, **kwargs):

        # check it in db
        with db.open_session() as s:
            dataset = self.dataset_service.dataset_dao.find_by_name(s, dataset_name)
            if dataset is not None:
                raise ValueError(f"Dataset {dataset_name} already exists ")

        # check it in file system
        dataset_dir = util.dataset_dir(dataset_name)
        if P.exists(dataset_dir):
            raise ValueError(f"Path {dataset_dir} already exists even dataset {dataset_name} not exists ")

        self.response_json({})


class DatasetPreviewDataHandler(BaseHandler):

    dataset_service = DatasetService()

    @gen.coroutine
    @authenticated
    def get(self, dataset_name, *args, **kwargs):

        # 1. validate param
        if dataset_name is None:
            raise IllegalParamException("dataset_name", None, "not empty")

        # page_num, page_size
        page_num = int(self.get_argument('page_num', 0))
        page_size = int(self.get_argument('page_size', 20))

        # 2. read file
        resp_preview_dataset = self.dataset_service.preview(dataset_name, page_num, page_size)

        # 3. response
        self.response_json(resp_preview_dataset.to_dict())


class TestImportFileHandler(BaseHandler):

    @gen.coroutine
    @authenticated
    def post(self, *args, **kwargs):
        path = self.get_request_as_dict_if_json().get("path")

        if path is None or len(path) == 0:
            raise ValueError("Param path can be empty.")

        path = P.abspath(path)
        if not P.exists(path):
            raise ValueError(f"{path} not exists.")

        if not P.isfile(path):
            raise ServiceException(CODE_NOT_FILE, f"{path} not file.")

        response = {}
        self.response_json(response)


class TemporaryDatasetHandler(BaseHandler):

    temporary_dataset_service = DatasetService()

    DEFAULT_SAMPLE_SIZE = 1000

    @gen.coroutine
    @authenticated
    def post(self, *args, **kwargs):
        # 1. read params
        req_dict = self.get_request_as_dict_if_json()

        # 2. create dataset
        temporary_dataset_name, analyze_data_job_name = self.temporary_dataset_service.create_temporary_dataset(req_dict)

        # 3. response
        response = \
            {
                "temporary_dataset_name": temporary_dataset_name,
                "analyze_job_name": analyze_data_job_name
            }
        self.response_json(response)


class DatasetAnalyzeProcessHandler(BaseHandler):

    dataset_service = DatasetService()

    @gen.coroutine
    @authenticated
    def post(self, dataset_name, analyze_job_name, *args, **kwargs):
        # 1. read param
        dict_body = self.get_request_as_dict_if_json()
        step = JobStep.load_dict(dict_body)
        self.dataset_service.add_analyze_process_step(dataset_name, analyze_job_name, step)

        # 2. response
        self.response_json({})

    @gen.coroutine
    @authenticated
    def get(self, dataset_name, analyze_job_name, *args, **kwargs):
        # 1. validate param
        if analyze_job_name is None:
            raise IllegalParamException("analyze_job_name", None, "not empty")

        # 2. query all the message of request_id  todo move to service
        with db.open_session() as s:
            messages = s.query(MessageEntity).filter(MessageEntity.author == analyze_job_name).order_by(MessageEntity.create_datetime.asc()).all()
            messages_dict_list = []
            for m in messages:
                messages_dict_list.append(util.loads(m.content))

        # 3. response
        response = \
            {
                "analyze_job_name": analyze_job_name,
                "temporary_dataset_name": dataset_name,
                "steps": messages_dict_list
            }
        self.response_json(response)


class InferTaskTypeHandler(BaseHandler):

    experiment_service = ExperimentService()
    dataset_service = DatasetService()

    @gen.coroutine
    @authenticated
    def post(self, dataset_name, *args, **kwargs):
        req_dict = self.get_request_as_dict_if_json()

        feature_name = util.require_in_dict(req_dict, 'feature_name', str)

        with db.open_session() as s:
            dataset = self.dataset_service.dataset_dao.require_by_name(s, dataset_name)
            features = Feature.load_dict_list(dataset.features)
            target_f = None
            for f in features:
                if f.name == feature_name:
                    target_f = f
                    break

            if target_f is None:
                raise ValueError(f"Feature name = {feature_name} not found. ")

            task_type = self.experiment_service._infer_task_type(target_f)

        resp = {"task_type": task_type,"feature_name": feature_name}

        self.response_json(resp)
