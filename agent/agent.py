# ------------------------------------------------------------------------------
# Copyright 2021 Mohammad Reza Golsorkhi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
# Name: agent.py
# Description: A agent that handles jobs and run jobs
# Version: 0.1.2
# Author: Mohammad Reza Golsorkhi
# ------------------------------------------------------------------------------


import datetime
import threading
from time import sleep

import agent.exceptions as exceptions
import agent.interrupt as interrupt
from agent.job import FunctionJob
import dill
import logging

logger = logging.getLogger(__name__)


class Agent:
    _name: str
    _initialized = False
    _Agent_counter = 0

    def __repr__(self):
        return f'Name : {self.name} agent_id : {self._id}'

    def __init__(self, daemon=True, name=None):
        # increment
        Agent._Agent_counter += 1

        self._id = Agent._Agent_counter
        self.jobs = []
        self._daemon = daemon
        self._started = threading.Event()
        self._is_stop = threading.Event()
        self._interrupt = interrupt.NoneInterrupt(self)
        self._jobs_id_counter = 0
        self._initialized = True
        self._name = str(name or Agent._newname())
        self.is_running = threading.Event()

    @staticmethod
    def _newname():
        return 'Agent-' + str(Agent._Agent_counter)

    def _agent(self):
        self.is_running.set()
        logger.info(msg=f'agent {self.name} started')
        while not self._is_stop.is_set():
            for job in self.jobs:
                if self._interrupt.is_set():
                    self._interrupt.lock.acquire()
                    self._interrupt.interrupt_handler()
                    self._interrupt.lock.release()
                    self._interrupt.clear()
                if (job.initialized is True) and (job.is_not_running.is_set() and job.is_enable) and (
                        job.next_run_time <= datetime.datetime.now()):
                    job.start(0.01)
            sleep(1)
        self.is_running.clear()
        logger.info(msg=f'agent {self.name} stopped')
        return 0

    def append_job(self, job):
        """
        load a job and add to jobs list
        :param job: a instance of job
        :return: None
        """
        self.jobs.append(job)

    def load_job(self):
        """
        place holder
        :return:
        """
        pass

    def loads_job(self):
        """
        place holder
        :return:
        """
        pass

    def dump_job(self):
        """
        place holder
        :return:
        """
        pass

    def dumps_job(self):
        """
        place holder
        :return:
        """
        pass

    def _add_job(self, func, options, is_enable, args, kwargs, name):
        self._jobs_id_counter += 1
        job_id = self._jobs_id_counter
        if name is None:
            name = 'job_' + str(job_id)
        if self.get_job_by_name(name) is not None:
            raise exceptions.DuplicateName('job name must be unique')

        self.jobs.append(FunctionJob(self, job_id, name, func, options, is_enable, args, kwargs))

    def create_job(self, func, options: dict, args=(), kwargs=None, is_enable: bool = True, name: str = None):
        self._add_job(func, options, is_enable, args, kwargs, name)

    def create_job_decorator(self, options: dict, args=(), kwargs=None, is_enable: bool = True, name: str = None):
        def decorator(func):
            self._add_job(func, options, is_enable, args, kwargs, name)
            return func

        return decorator

    def get_job_by_name(self, job_name: str):
        for job in self.jobs:
            if job.name == job_name:
                return job
        else:
            return None

    def get_job_by_id(self, job_id: int):
        for job in self.jobs:
            if job.status['job_id'] == job_id:
                return job
        else:
            return None

    @staticmethod
    def run_job(job: FunctionJob, timeout=None):
        if job:
            job.start(timeout)
            return 1
        else:
            return 0

    def run_job_by_name(self, job_name: str, timeout=None):
        job = self.get_job_by_name(job_name)
        if job:
            job.start(timeout)
            return 1
        else:
            return 0

    def run_job_by_id(self, job_id: int, timeout=None):
        job = self.get_job_by_id(job_id)
        if job:
            job.start(timeout)
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

        logger.info(msg=f'agent {self.name} is starting')
        threading.Thread(target=self._agent, daemon=self._daemon, name=self._name).start()
        self._is_stop.clear()
        self._started.set()

    def stop(self):
        if not self._initialized:
            raise RuntimeError("Agent.__init__() not called")
        if not self._started.is_set():
            raise RuntimeError("cannot stop Agent before it is started")
        logger.info(msg=f'agent {self.name} is stopping')
        self._interrupt = interrupt.StopInterrupt(self)
        self._interrupt.set()
        self._interrupt.wait()
        self._is_stop.set()
        self._started.clear()
        logger.info(msg=f'agent {self.name} stopped')

    # def __del__(self):
    #     if not self._is_stop.is_set():
    #         self.stop()
    #     for job in self.jobs:
    #         if not job.is_not_running.is_set():
    #             job.stop(timeout=0, silence_error=0)
    #     self.jobs.clear()

    @property
    def interrupt(self):
        if not self._initialized:
            raise RuntimeError("Agent.__init__() not called")
        return self._interrupt

    @interrupt.setter
    def interrupt(self, val):
        if self._interrupt is not None:
            if self._interrupt.lock.locked():
                logger.error(msg='interrupt is set waiting for interrupt clear')
                self._interrupt.lock.acquire()
                self._interrupt.lock.release()
        self._interrupt = val

    @property
    def name(self):
        """A string used for identification purposes only.
        It has no semantics. Multiple threads may be given the same name. The
        initial name is set by the constructor.
        """
        if not self._initialized:
            raise RuntimeError("Agent.__init__() not called")
        return self._name

    @name.setter
    def name(self, val: str):
        if not self._initialized:
            raise RuntimeError("Agent.__init__() not called")

        if self._started:
            raise PermissionError('cannot set name of active Agent')
        else:
            self._name = val
