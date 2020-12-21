# -*- encoding: utf-8 -*-
import threading
import time
import psutil
from psutil import _common as ps_cons

from cooka.common.model import Model, JobStep, TrainStep
from cooka.service.experiment_service import ExperimentService
from cooka.common.log import log_web as logger


class ProcessMonitor(threading.Thread):
    """
    Fix some process end but never send back event sometimes , such as server restart
    """

    experiment_service = ExperimentService()

    def __init__(self):
        super(ProcessMonitor, self).__init__(name="ProcessMonitorThread", daemon=True)  # stop if parent Thread finished
        self.process_status_mapping = {}

    def run(self) -> None:
        logger.info("[MonitorThread] loop running...")
        while 1:
            time.sleep(1)
            # 1. select all running models
            models = self.experiment_service.find_running_model()

            # 2. check process of running model
            self.handle_models(models)

    def handle_models(self, models: list):
        for m in models:
            m: Model = m
            pid = m.pid
            if pid is None:
                pass
                # logger.warning(f"Model {m.name} , training process pid is None. ")
            else:
                try:
                    status = psutil.Process(pid).status()
                    if pid not in self.process_status_mapping:
                        self.process_status_mapping[pid] = status
                        logger.info(f"Model {m.name} , pid is {pid} process status is {status} ")
                    else:
                        if self.process_status_mapping[pid] != status:
                            logger.info(f"Model {m.name} , pid is {pid} process status changed from{ self.process_status_mapping[pid] } to {status} ")
                            self.process_status_mapping[pid] = status
                except Exception as e:   # usually is NoSuchProcess
                    # update if process finished
                    logger.warning(f"Model {m.name} , training process pid = {pid} not exists. ")
                    self.experiment_service.train_process_terminated(m.name)
