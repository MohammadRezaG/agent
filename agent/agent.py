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
# name: agent.py
# Description: A agent that handles jobs and run jobs
# Version: 0.1.2
# Author: Mohammad Reza Golsorkhi
# ------------------------------------------------------------------------------


import datetime
import threading
from time import sleep

import agent.exceptions as exceptions
import agent.interrupt as _interrupt
from agent.job import FunctionJob
import logging

try:
    import dill as pickle
except ImportError:
    import pickle

logger = logging.getLogger(__name__)


class Agent:
    _name: str
    _initialized = False
    _Agent_counter = 0

    def __repr__(self):
        return f'name : {self.name} agent_id : {self._id}'

    def __init__(self, daemon=True, name=None, **jobs_variables):
        # increment
        Agent._Agent_counter += 1

        self._id = Agent._Agent_counter
        self.jobs = []
        self._daemon = daemon
        self._started = threading.Event()
        self._is_stop = threading.Event()
        self._interrupt = _interrupt.NoneInterrupt(self)
        self._jobs_id_counter = 0

        self._name = str(name or Agent._newname())
        self.is_running = threading.Event()
        self.__dict__.update(jobs_variables)
        self._initialized = True

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

    def _add_job(self, func, options, is_enable, args, kwargs, name, **job_variables):
        self._jobs_id_counter += 1
        job_id = self._jobs_id_counter
        if name is None:
            name = 'job_' + str(job_id)
        if self.get_job_by_name(name) is not None:
            raise exceptions.DuplicateName('job name must be unique')

        self.jobs.append(FunctionJob(self, job_id, name, func, options, is_enable, args, kwargs, **job_variables))

    def create_job(self, func, options: dict, args=(), kwargs=None, is_enable: bool = True, name: str = None,
                   **job_variables):
        self._add_job(func, options, is_enable, args, kwargs, name, **job_variables)

    def create_job_decorator(self, options: dict, args=(), kwargs=None, is_enable: bool = True, name: str = None,
                             **job_variables):
        def decorator(func):
            self._add_job(func, options, is_enable, args, kwargs, name, **job_variables)
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
        """
        start agent inner thread
        :return: None
        """
        if not self._initialized:
            raise RuntimeError("Agent.__init__() not called")

        if self._started.is_set():
            raise RuntimeError("Agent can only be started once")

        logger.info(msg=f'agent {self.name} is starting')
        threading.Thread(target=self._agent, daemon=self._daemon, name=self._name).start()
        self._is_stop.clear()
        self._started.set()

    def stop(self):
        """
        set a stop interrupt that wait for all running job stop
        :return: None
        """
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

    @property
    def interrupt(self):
        """
        you can active a interrupt whit .set() methode
        :return:
        """
        if not self._initialized:
            raise RuntimeError("Agent.__init__() not called")
        return self._interrupt

    @interrupt.setter
    def interrupt(self, val: _interrupt.BaseInterrupt):
        """
        set a interrupt that can be activate whit interrupt.set() methode
        :param val: get a class that inherited BaseInterrupt
        you can find it in agent.interrupt
        :return:
        """
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

    @property
    def info(self):
        """
        get info about agent
        :return: dict of info
        """
        return {
            'version': '0.1.2',
            'is_dill_sported': getattr(pickle, 'info')

        }
