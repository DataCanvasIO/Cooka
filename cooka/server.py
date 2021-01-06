# -*- encoding: utf-8 -*-
from types import CodeType

import tornado.ioloop
import tornado.web

from os import path as P
from tornado import web

from cooka.common import consts
from cooka.common.log import log_web as logger

from cooka.dao.entity import initialize_database

from cooka.handler.dataset_handler import TemporaryDatasetHandler, DatasetAnalyzeProcessHandler, InferTaskTypeHandler
from cooka.handler.resource_handler import TextResourceHeadHandler, TextResourceTailHandler, ResourceHandler, AssetsHandler, StreamResourceHandler
from cooka.handler.dataset_handler import DatasetHandler, DatasetItemHandler, DatasetPreviewDataHandler, TestImportFileHandler, DatasetNameHandler
from cooka.handler.experiment_handler import ModelDetailHandler, ExperimentHandler, ModelTrainProcessHandler, RecommendTrainConfigurationHandler
from cooka.handler.model_serving_handler import BatchPredictJobHandler, BatchPredictJobItemHandler
from cooka.handler.sys_hander import ConfigHandler
from cooka.service.process_monitor import ProcessMonitor
import os
import argparse


class CookaWebApplication(web.Application):

    def __init__(self, database_path):
        # 1. init handlers
        handlers = self.init_handlers()

        # 2. check database
        if not P.exists(database_path):
            database_dir = P.dirname(database_path)
            if not P.exists(database_dir):
                os.makedirs(database_dir, exist_ok=True)

            initialize_database()
            logger.info(f"Initialize database file {database_path}")

        static_path = P.join(P.dirname(P.abspath(__file__)), 'assets')
        # super(CookaApp, self).__init__(handlers, debug=True, static_path=static_path, static_url_prefix='/')
        super(CookaWebApplication, self).__init__(handlers, debug=False)

    def init_handlers(self):
        static_path = P.join(P.dirname(P.abspath(__file__)), 'assets')
        handlers = [
            (r'/api/dataset/(?P<dataset_name>.+)/feature-series/default/train-job/(?P<no_training>.+)/model/(?P<model_name>.+)', DatasetItemHandler),
            (r"/api/dataset/(?P<dataset_name>.+)/analyze-job/(?P<analyze_job_name>.+)", DatasetAnalyzeProcessHandler),

            (r'/api/dataset', DatasetHandler),
            (r'/api/sysconfig', ConfigHandler),
            (r"/api/temporary-dataset", TemporaryDatasetHandler),

            (r"/api/dataset/(?P<dataset_name>.+)/preview", DatasetPreviewDataHandler),
            (r"/api/dataset/(?P<dataset_name>.+)/infer-task-type", InferTaskTypeHandler),
            (r"/api/dataset/(?P<dataset_name>.+)/check-name", DatasetNameHandler),

            (r'/api/dataset/(?P<dataset_name>.+)/feature-series/default/train-job', ExperimentHandler),
            (r'/api/dataset/(?P<dataset_name>.+)/feature-series/default/recommend-train-conf', RecommendTrainConfigurationHandler),
            (r'/api/dataset/(?P<dataset_name>.+)/feature-series/default/train-job/(?P<train_job_name>.+)', ModelTrainProcessHandler),

            (r'/api/dataset/test-import-file', TestImportFileHandler),
            # /api/dataset/bankdata/feature-series/default/model/bankdata_DeepTables_20200929162656239705/batch-predict-job
            (r'/api/dataset/(?P<dataset_name>.+)/feature-series/default/model/(?P<model_name>.+)/batch-predict-job', BatchPredictJobHandler),
            (r'/api/dataset/(?P<dataset_name>.+)/feature-series/default/model/(?P<model_name>.+)/batch-predict-job/(?P<batch_predict_job_name>.+)', BatchPredictJobItemHandler),

            (r'/api/dataset/(?P<dataset_name>.+)/feature-series/default/model/(?P<model_name>.+)', ModelDetailHandler),

            (r"/api/dataset/(?P<dataset_name>.+)", DatasetItemHandler),  # low priority

            (r"/api/resource/(?P<path>.+)", TextResourceHeadHandler),
            # (r"/api/resource/(?P<path>.+)/tail", TextResourceTailHandler),

            (r"/api/resource", StreamResourceHandler),
            # (r"/api/resource", ResourceHandler),
            (r'/(.*?)$', AssetsHandler, {"path": static_path}),  # lowest priority
        ]

        return handlers


def make_app():
    return CookaWebApplication(consts.PATH_DATABASE)


def start_server():
    # 1. create web app
    application = CookaWebApplication(consts.PATH_DATABASE)
    application.listen(consts.SERVER_PORT)

    # 2. start thread
    pm = ProcessMonitor()
    pm.start()

    # 3. start io loop
    logger.info(f"Cooka running at: http://0.0.0.0:{consts.SERVER_PORT}")
    tornado.ioloop.IOLoop.instance().start()

