import os
from multiprocessing import Manager, Pool

import abc, subprocess
import threading
import time

from os import path as P
from cooka.common.log import log_core as logger
from multiprocessing import Process
from threading import Condition
from multiprocessing import Queue
from cooka.common.util import short_uuid


class CommandProcess(metaclass=abc.ABCMeta):

    def __init__(self, command, logfile, env=None, id=None):
        self.command = command
        self.logfile = logfile
        self.env = env
        self.pid = None

        if id is None:
            id = short_uuid()
        self.id = id

    def execute(self):
        """ Process body

        Args:
            in_queue: blocking queue
            out_queue:

        Returns:

        """

        log_dir = P.dirname(self.logfile)
        if not P.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        logger.info(f"Run command{self.command}, log file at: {self.logfile}")

        with open(self.logfile, 'w') as f:
            time_start = time.time()
            # 1. start process
            proc = subprocess.Popen(self.command, shell=True, stdout=f, stderr=f, bufsize=-1, env=self.env)
            self.pid = proc.pid

            # 2. update status
            # r1 = Process.objects.filter(id=self.id).update(status=Process.Status.Running,
            #                                                pid=self.pid,
            #                                                returncode=proc.returncode,
            #                                                update_date_time=datetime.datetime.now())
            # if r1 < 1:  # update nothing
            #     raise Exception(f"Process id={self.id}, command=${self.command} running but does not create in db.")

            # 3. wait for end
            while proc.poll() is None:
                time.sleep(0.1)
            if proc.returncode != 0:
                logger.error(f"Process run failed, returncode is {proc.returncode}, the log at:{self.logfile}")

            returncode = proc.returncode

        return returncode

            # # 4. todo update status
            # r2 = Process.objects.filter(id=self.id).update(status=Process.Status.Finished,
            #                                                returncode=proc.returncode,
            #                                                update_date_time=now(),
            #                                                duration= time_end - time_start)

            # if r2 < 1:  # update nothing
            #     raise Exception(f"Process id={self.id}, command=${self.command} finished but does not create in db.")

    def async_run(self):
        # 1. create in db
        # p = Process(id=self.id,
        #             command=self.command,
        #             logfile=self.logfile,
        #             status=Process.Status.Ready,
        #             create_date_time=datetime.datetime.now(),
        #             update_date_time=datetime.datetime.now())
        # p.save()

        # 2. start process
        t = threading.Thread(target=self.execute)
        t.start()

    def run(self):
        # # 1. create in db
        # p = Process(id=self.id,
        #             command=self.command,
        #             logfile=self.logfile,
        #             status=Process.Status.Ready,
        #             create_date_time=now(),
        #             update_date_time=now())
        # p.save()

        return self.execute()


class PipeQueue:

    def __init__(self, maxsize=100):
        self.q = Queue(maxsize)  # Use aggregation but extends, because `Queue` is a method not class

    def get_all(self):
        messages = []
        try:
            while 1:
                message = self.q.get(block=False)
                messages.append(message)
        except BaseException:  # Linux Python has no: from _queue import Empty
            pass
            # No message
        return messages

    def put(self, obj):
        self.q.put(obj)


class ProcessJob(Process):

    def __init__(self):
        self.output_queue = PipeQueue()
        super(ProcessJob, self).__init__()

    @abc.abstractmethod
    def _run(self):
        pass

    def run(self):
        try:  # resolve no log when occur error
            self._run()
        except BaseException as e:
            logger.exception(e)

    @abc.abstractmethod
    def _on_receive_message(self, message):
        """Run in process manager thread ,web process"""
        pass

    def on_receive_message(self, message):
        """Run in process manager thread ,web process"""
        self._on_receive_message(message)

    @abc.abstractmethod
    def _on_finish(self, return_code):
        """Run in process manager thread ,web process"""
        pass

    def on_finish(self, return_code):
        # Fix one case process has already finish but message not handle over, last check before finish
        messages = self.output_queue.get_all()
        logger.info(f"Finish, check queue: {messages}, returncode={return_code}")
        for m in messages:
            self.on_receive_message(m)

        self._on_finish(return_code)

