# -*- encoding: utf-8 -*-
from cooka.common.exceptions import IllegalParamException, MissingParamException, EntityNotExistsException
from cooka.common import util
from cooka.common import consts
from cooka.common.model import ExperimentConf, CrossValidation, TrainValidationHoldout
from cooka.dao import db

from cooka.handler.base_handler import BaseHandler
from tornado import gen

from cooka.common.model import DatasetStats
from cooka.service.dataset_service import DatasetService
from os import path as P
import os

from cooka.service.experiment_service import ExperimentService
from cooka.common.authentication import authenticated


class ExperimentHandler(BaseHandler):
    experiment_service = ExperimentService()

    @authenticated
    @gen.coroutine
    def post(self, dataset_name, *args, **kwargs):
        request_body = self.get_request_as_dict_if_json()
        request_body['dataset_name'] = dataset_name

        config = self.experiment_service.experiment(request_body)
        self.response_json(config)

    @authenticated
    @gen.coroutine
    def get(self, dataset_name, *args, **kwargs):
        # page_num, page_size

        page_num = int(self.get_argument('page_num', 1))
        page_size = int(self.get_argument('page_size', 20))

        experiments, total = self.experiment_service.get_experiments(dataset_name, page_num, page_size)
        r = {
            "experiments": experiments,
            "count": total,
            "notebook_portal": consts.NOTEBOOK_PORTAL
        }
        self.response_json(r)


class ModelDetailHandler(BaseHandler):

    experiment_service = ExperimentService()

    @authenticated
    @gen.coroutine
    def get(self, dataset_name, model_name, *args, **kwargs):
        m = self.experiment_service.retrieve(model_name)
        self.response_json(m)


class ModelTrainProcessHandler(BaseHandler):

    experiment_service = ExperimentService()

    @authenticated
    @gen.coroutine
    def post(self, dataset_name, train_job_name, *args, **kwargs):
        # 1. read param
        req_dict = self.get_request_as_dict_if_json()
        self.experiment_service.add_train_process_step(train_job_name, req_dict)

        # 2. response
        self.response_json({})

    @authenticated
    @gen.coroutine
    def get(self, temporary_dataset_name, analyze_job_name, *args, **kwargs):
        pass
        # 1. validate param
        # if analyze_job_name is None:
        #     raise IllegalParamException("analyze_job_name", None, "not empty")
        #
        # # 2. query all the message of request_id
        # with db.open_session() as s:
        #     messages = s.query(MessageEntity).filter(MessageEntity.author == analyze_job_name).order_by(MessageEntity.create_datetime.asc()).all()
        #
        #     messages_dict_list = []
        #
        #     for m in messages:
        #         messages_dict_list.append(util.loads(m.content))
        #
        # # 3. response
        # response = \
        #     {
        #         "analyze_job_name": analyze_job_name,
        #         "steps": messages_dict_list
        #     }
        # self.response_json(response)


class RecommendTrainConfigurationHandler(BaseHandler):

    experiment_service = ExperimentService()

    @authenticated
    @gen.coroutine
    def post(self, dataset_name, *args, **kwargs):
        req_dict = self.get_request_as_dict_if_json()
        conf = self.experiment_service.recommended_train_configuration(dataset_name, req_dict)
        data = \
            {
                "conf": conf
            }
        self.response_json(data)
