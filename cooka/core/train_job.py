# -*- encoding: utf-8 -*-

# from cooka.common import util
# from cooka.common.log import log_core as logger
# from cooka.common.model import DatasetStats
# from cooka.common.model import TrainJobConf, TrainStep, ExperimentConf, FrameworkType, \
#     JobStep
# from cooka.core.process_manager import PipeQueue, ProcessJob
# from cooka.core.trainer import GBMTrainer, DeepTablesTrainer
#
#
# class TrainProcessJob(ProcessJob):
#
#     def __init__(self, dataset_stats: DatasetStats, model_name: str, experiment_conf: ExperimentConf, train_job_conf: TrainJobConf, experiment_service):
#         self.dataset_stats = dataset_stats
#         self.model_name = model_name
#         self.experiment_conf = experiment_conf
#         self.train_job_conf = train_job_conf
#         self.experiment_service = experiment_service  # todo replace to HTTP api not service for distribut
#         super(TrainProcessJob, self).__init__()
#
#     def _run(self) -> None:
#         make_trainer(self.dataset_stats, self.model_name, self.experiment_conf, self.train_job_conf, self.output_queue).train()
#
#     def _on_receive_message(self, step: TrainStep):
#         self.experiment_service.add_train_process_step(self.model_name, step)
#
#     def _on_finish(self, return_code):
#         logger.info("Train finished.")
#
#
# def make_trainer(dataset_stats: DatasetStats, model_name, experiment_conf: ExperimentConf, train_job_conf: TrainJobConf, output_queue: PipeQueue):
#     if train_job_conf.framework == FrameworkType.GBM:
#         trainer = GBMTrainer(dataset_stats, model_name,  experiment_conf, train_job_conf, output_queue)
#     elif train_job_conf.framework == FrameworkType.DeepTables:
#         trainer = DeepTablesTrainer(dataset_stats,  model_name,  experiment_conf, train_job_conf, output_queue)
#     else:
#         raise ValueError(f"Unknown framework: {train_job_conf.framework}")
#     return trainer
