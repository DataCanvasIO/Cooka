# -*- encoding: utf-8 -*-
from cooka.common import util
from cooka.common.exceptions import EntityNotExistsException
from cooka.common.model import JobStep, Model, PredictStepType
from cooka.dao import db
from cooka.dao.dao import ExperimentDao, DatasetDao
from cooka.dao.entity import MessageEntity
from cooka.common import consts
import sys, os
from cooka.common.log import log_web as logger
from os import path as P


class ModelServingService:

    model_dao = ExperimentDao()
    dataset_dao = DatasetDao()

    def predict(self, dataset_name, model_name, req_dict: dict):
        # 1. read params
        file_path = util.require_in_dict(req_dict, 'file_path', str)
        reserved_cols = util.get_from_dict(req_dict, 'reserved_cols', list)
        upload_took = util.require_in_dict(req_dict, 'upload_took', float)

        if reserved_cols is None or len(reserved_cols) < 1:
            reserved_cols_str = ""
        else:
            reserved_cols_str = ",".join(reserved_cols)

        # 2.  check params
        with db.open_session() as s:
            self.model_dao.require_by_name(s, model_name).to_model_bean()
            dataset_stats = self.dataset_dao.require_by_name(s, dataset_name).to_dataset_stats()
        predict_job_name = util.predict_job_name(dataset_name)
        abs_file_path = P.join(consts.DATA_DIR, file_path)
        if not P.exists(abs_file_path):
            raise ValueError(f"Input file not exists: {abs_file_path}")
        if not P.isfile(abs_file_path):
            raise ValueError(f"Input file is not file: {abs_file_path}")

        # 3. add upload step
        upload_extension = {
            "file_size": P.getsize(abs_file_path)
        }
        upload_step = JobStep(type=PredictStepType.Upload, status=JobStep.Status.Succeed, took=upload_took, datetime=util.get_now_long(), extension=upload_extension)
        self.add_predict_process_step(model_name, predict_job_name, upload_step)

        # 4.  execute command
        model_dir = util.model_dir(dataset_name, model_name)
        predict_log_path = P.join(model_dir, f"{predict_job_name}.log")
        if not dataset_stats.has_header:
            default_headers = ",".join([f.name for f in dataset_stats.features])
        else:
            default_headers = None

        command = f"nohup {sys.executable} {consts.PATH_INSTALL_HOME}/cooka/core/batch_predict_job.py --input_file_path={abs_file_path} --reserved_cols={reserved_cols_str} --model_name={model_name} --dataset_name={dataset_name} --job_name={predict_job_name} --has_header={dataset_stats.has_header} --default_headers={default_headers}  --server_portal={consts.SERVER_PORTAL} 1>{predict_log_path} 2>&1 &"

        logger.info(f"Run analyze job command: \n{command}")
        logger.info(f"Log file:\ntail -f {predict_log_path}")
        os.system(command)  # ha ha ha

        return predict_job_name

    def add_predict_process_step(self, model_name: str, job_name: str, step: JobStep):
        step_type = step.type
        with db.open_session() as s:
            # 1.  check temporary model exists
            model = self.model_dao.require_by_name(s, model_name)

            # 2. check event type, one type one record
            messages = s.query(MessageEntity).filter(MessageEntity.author == job_name).all()
            for m in messages:
                if step_type == util.loads(m.content).get('type'):
                    raise Exception(f"Event type = {step_type} already exists .")

            # 3. create a new message
            content = util.dumps(step.to_dict())
            message = MessageEntity(id=util.short_uuid(), author=job_name, content=content, create_datetime=util.get_now_datetime())
            s.add(message)

            # 4. handle analyze event
            # todo check status change
