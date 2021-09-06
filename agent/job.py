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
# Name: job.py
# Description: run its inner function when started
# Version: 0.1.
# Author: Mohammad Reza Golsorkhi
# ------------------------------------------------------------------------------


import threading

from threading import Thread, Event
import datetime
from inspect import signature
from enum import Enum
from agent.handler import Cnrt, JobFailHandler, JobSuccessHandler
from agent.exceptions import JobNotRunning
import logging


class LastRuntimeState(Enum):
    never_executed = 0
    success = 1
    failed = 2


class Job:
    _initialized = False

    def __repr__(self):
        return str(self.status)

    def __str__(self):
        return f'Name : {self.name} job_id : {self.id} agent : {self._agent}'

    def __init__(self, agent, job_id, name, func, options, is_enable, args, kwargs):

        logging.log(level=logging.INFO, msg=f'initializing job {name}')
        self._id = job_id
        self._name = name
        self._agent = agent
        self._fail_count = 0
        self.status = {}
        self.update_status()
        self.options = options
        self._func = func
        self.next_run_time = None
        self._calculate_next_run_time = Cnrt(self, options)
        self._job_fail_handler = JobFailHandler(self, options=self.options)
        self._job_success_handler = JobSuccessHandler(self, options=self.options)
        self.next_run_time = self._calculate_next_run_time()
        self._is_not_running = Event()
        self._is_not_running.set()
        self.is_enable = is_enable
        self.job_thread = threading.Thread()
        self._args = args

        func_sig = signature(self._func)
        self._kwargs = kwargs
        if kwargs is None:
            self._kwargs = {}
        if (len(self._args) + len(self._kwargs) < len(func_sig.parameters)) and func_sig.parameters.get(
                'job') is not None:
            self._kwargs = {**self._kwargs, **{'job': self}}

        if (len(self._args) + len(self._kwargs) < len(func_sig.parameters)) and func_sig.parameters.get(
                'agent') is not None:
            self._kwargs = {**self._kwargs, **{'agent': agent}}

        self._initialized = True

        logging.log(level=logging.INFO, msg=f'job {name} has initialized')

    def _job_run(self):
        try:
            self._is_not_running.clear()
            logging.log(level=logging.INFO, msg=f'starting job {self._name}')
            self._calculate_next_run_time()
            logging.log(level=logging.INFO, msg=f'executing job {self._name} function')
            self.status['last_return'] = self._func(*self._args, **self._kwargs)
        except Exception as E:
            print(E)
            self._fail_count += 1
            self.status['LastRunState'] = LastRuntimeState.failed
            logging.log(level=logging.ERROR, msg=f'job: {self.name} Failed to Execute du\n', exc_info=True)
            self._job_fail_handler(exception=E)
            return 0
        else:
            self._fail_count = 0
            self._job_success_handler()
            logging.log(level=logging.INFO, msg=f'job {self.name} execute successfully')
            self.status['LastRunState'] = LastRuntimeState.success
        finally:
            self.status['LastRuntime'] = datetime.datetime.now()
            self.update_status()
            self._is_not_running.set()
            logging.log(level=logging.DEBUG, msg=str(self.status))

    def stop(self, timeout: float = 10, silence_error=None):
        """
        stop job Thread if is _is_not_running == False
        this function use threading join for stopping the Job Thread
        if _is_not_running == True this function raise JobNotRunning but you can use silence_error

        if silence_error Not None than return  silence_error
        :param timeout: wait before kill job Thread by default is set to 10
        :param silence_error: None for raise JobNotRunning() or return silence_error if not none
        :return: 1 if successful None if not
        """
        if not self._is_not_running.is_set():
            self.job_thread.join(timeout=timeout)
            return 1
        else:
            if silence_error:
                return None
            raise JobNotRunning()

    def start(self, timeout=None):
        """
        start job in a another Thread whit name of job
        by default daemon is set to True you can change this in options
        :return: 1 if successful
        """
        if not self.is_not_running.is_set():
            logging.log(level=logging.WARNING, msg=f'job {self.name} is running whiting for job to done')
            if not self.is_not_running.wait(timeout=timeout):
                logging.log(level=logging.WARNING, msg=f'timeout occurred on job{self.name}')

        self.job_thread = Thread(target=self._job_run, daemon=self.options.get('daemon', True), name=self._name)
        self.job_thread.start()
        return 1

    def update_status(self):
        self.status.update({
            'job_id': self._id,
            'name': self._name,
            'LastRunState': LastRuntimeState.never_executed,
            'LastRuntime': None,
            'fail_count': self._fail_count
        })

    @property
    def agent(self):
        assert self._initialized, "job.__init__() not called"
        return self._agent

    @agent.setter
    def agent(self, val):
        if not self._initialized:
            raise RuntimeError("job.__init__() not called")

        if not self._is_not_running.is_set():
            raise PermissionError('cannot assign active job to another agent')
        else:
            self._agent = val

    @property
    def fail_count(self):
        assert self._initialized, "job.__init__() not called"
        return self._fail_count

    @property
    def is_not_running(self):
        assert self._initialized, "job.__init__() not called"
        return self._is_not_running

    @is_not_running.setter
    def is_not_running(self, val):
        raise PermissionError('cannot set job.is_not_running')

    @property
    def name(self):
        assert self._initialized, "job.__init__() not called"
        return self._name

    @name.setter
    def name(self, val):
        if not self._initialized:
            raise RuntimeError("Agent.__init__() not called")

        if not self._is_not_running.is_set():
            raise PermissionError('cannot set name of active job')
        else:
            self._name = val

    @property
    def id(self):
        assert self._initialized, "job.__init__() not called"
        return self._id

    @id.setter
    def id(self, val):
        raise PermissionError('cannot set job.id')

    @property
    def initialized(self):
        return self._initialized

    @initialized.setter
    def initialized(self, val):
        raise PermissionError('cannot set job.initialized')
