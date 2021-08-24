import datetime
import threading
import time

import exceptions
import interrupt
from job import Job
import logging


class Agent:
    _name: str
    _initialized = False
    _Agent_counter = 0
    logger = None

    def __init__(self, daemon=True, name=None):
        # increment
        Agent._Agent_counter += 1

        self._id = Agent._Agent_counter
        if Agent.logger is None:
            Agent.get_logger()
        self._logger = Agent.logger
        self.jobs = []
        self._daemon = daemon
        self._started = threading.Event()
        self._is_stop = threading.Event()
        self._interrupt = interrupt.NoneInterrupt()
        self._jobs_id_counter = 0
        self._initialized = True
        self._name = str(name or Agent._newname())
        self.is_running = threading.Event()

    @staticmethod
    def _newname():
        return 'Agent-' + str(Agent._Agent_counter)

    def _agent(self):
        self.is_running.set()
        self._logger.info('agent started')
        while not self._is_stop.is_set():
            for job in self.jobs:
                if (job.initialized is True) and (not job.is_running.is_set() and job.is_enable) and (
                        job.next_run_time <= datetime.datetime.now()):
                    job.start()
                if self._interrupt.is_set():
                    self._interrupt.interrupt_handler()
                    self._interrupt.clear()
            time.sleep(1)
        self.is_running.clear()
        return 0

    @staticmethod
    def get_logger():

        Agent.logger = logging.getLogger(__name__)

        agent_format = "%(threadName)s: %(asctime)s - %(name)s - %(levelname)s - %(message)s"
        debug_format = "%(processName)s %(threadName)s: %(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(fmt=agent_format)
        debug_formatter = logging.Formatter(fmt=debug_format)
        # Create handlers
        agent_handler = logging.FileHandler('agent.log')
        c_handler = logging.StreamHandler()
        debug_handler = logging.FileHandler('agent_debug.log')

        agent_handler.setLevel(logging.INFO)
        c_handler.setLevel(logging.ERROR)
        debug_handler.setLevel(logging.DEBUG)

        agent_handler.setFormatter(formatter)
        c_handler.setFormatter(formatter)
        debug_handler.setFormatter(debug_formatter)

        Agent.logger.addHandler(agent_handler)
        Agent.logger.addHandler(c_handler)
        Agent.logger.addHandler(debug_handler)
        Agent.logger.setLevel(logging.ERROR)
        return Agent.logger

    def _add_job(self, func, option, is_enable, args, kwargs, name):
        self._jobs_id_counter += 1
        job_id = self._jobs_id_counter
        if name is None:
            name = 'job_' + str(job_id)
        if self.get_job_by_name(name) is not None:
            raise exceptions.DuplicateName('job name must be unique')

        self.jobs.append(Job(self, job_id, name, func, option, is_enable, args, kwargs))

    def create_job(self, func, option: dict, args=(), kwargs=None, is_enable: bool = True, name: str = None):
        self._add_job(func, option, is_enable, args, kwargs, name)

    def create_job_decorator(self, option: dict, args=(), kwargs=None, is_enable: bool = True, name: str = None):
        def decorator(func):
            self._add_job(func, option, is_enable, args, kwargs, name)
            return func

        return decorator

    def get_job_by_name(self, job_name: str):
        for job in self.jobs:
            if job.status['name'] == job_name:
                return job
        else:
            return None

    def get_job_by_id(self, job_id: int):
        for job in self.jobs:
            if job.status['job_id'] == job_id:
                return job
        else:
            return None

    def run_job_by_name(self, job_name: str):
        job = self.get_job_by_name(job_name)
        if job:
            job.start()
            return 1
        else:
            return 0

    def run_job_by_id(self, job_id: int):
        job = self.get_job_by_id(job_id)
        if job:
            job.start()
            return 1
        else:
            return 0

    def get_all_jobs(self):
        return self.jobs

    def get_all_running_jobs(self):
        return [job for job in self.jobs if job.is_running.is_set()]

    def start(self):
        if not self._initialized:
            raise RuntimeError("Agent.__init__() not called")

        if self._started.is_set():
            raise RuntimeError("Agent can only be started once")

        self._logger.info('agent starting')
        threading.Thread(target=self._agent, daemon=self._daemon).start()
        self._started.set()

    def stop(self):
        if not self._initialized:
            raise RuntimeError("Agent.__init__() not called")
        if not self._started.is_set():
            raise RuntimeError("cannot stop Agent before it is started")
        self._logger.info('agent stopping')
        self._interrupt = interrupt.StopInterrupt(self)
        self._interrupt.set()
        self._interrupt.wait()
        self._is_stop.set()
        self._started.clear()
        self._logger.info('agent stopped')

    @property
    def name(self):
        """A string used for identification purposes only.

        It has no semantics. Multiple threads may be given the same name. The
        initial name is set by the constructor.

        """
        assert self._initialized, "Agent.__init__() not called"
        return self._name

    @name.setter
    def name(self, val: str):
        if not self._initialized:
            raise RuntimeError("Agent.__init__() not called")

        if self._started:
            raise PermissionError('cannot set name of active Agent')
        else:
            self._name = val
