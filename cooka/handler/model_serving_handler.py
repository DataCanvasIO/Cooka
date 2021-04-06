# -*- encoding: utf-8 -*-

from tornado import gen

from cooka.common import util
from cooka.common.authentication import authenticated
from cooka.common.model import JobStep
from cooka.dao import db
from cooka.dao.entity import MessageEntity
from cooka.handler.base_handler import BaseHandler
from cooka.service.model_serving_service import ModelServingService


class BatchPredictJobItemHandler(BaseHandler):

    model_serving_service = ModelServingService()

    @authenticated
    @gen.coroutine
    def get(self, dataset_name, model_name, batch_predict_job_name, *args, **kwargs):
        # 1. query all the message of request_id  todo move to service
        with db.open_session() as s:
            messages = s.query(MessageEntity).filter(MessageEntity.author == batch_predict_job_name).order_by(MessageEntity.create_datetime.asc()).all()
            messages_dict_list = []
            for m in messages:
                messages_dict_list.append(util.loads(m.content))

        # 2. response
        response = \
            {
                "batch_predict_job_name": batch_predict_job_name,
                "dataset_name": dataset_name,
                "steps": messages_dict_list
            }
        self.response_json(response)

    @authenticated
    @gen.coroutine
    def post(self, dataset_name, model_name, batch_predict_job_name, *args, **kwargs):

        # 1. read param
        dict_body = self.get_request_as_dict_if_json()
        step = JobStep.load_dict(dict_body)
        self.model_serving_service.add_predict_process_step(model_name, batch_predict_job_name, step)

        # 2. response
        self.response_json({})


class BatchPredictJobHandler(BaseHandler):

    model_serving_service = ModelServingService()

    @authenticated
    @gen.coroutine
    def post(self, dataset_name, model_name, *args, **kwargs):
        request_body = self.get_request_as_dict_if_json()
        predict_job_name = self.model_serving_service.predict(dataset_name, model_name, request_body)
        self.response_json({"batch_predict_job_name": predict_job_name})
