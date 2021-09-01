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
# Version: 0.0.5
# Author: Mohammad Reza Golsorkhi
# ------------------------------------------------------------------------------


import threading

from threading import Thread, Event
import datetime
from inspect import signature
from enum import Enum
from handler import Cnrt, JobFailHandler
from exceptions import DuplicateName, JobNotRunning


class LastRuntimeState(Enum):
    never_executed = 0
    success = 1
    failed = 2


class Job:
    logger = None
    _initialized = False

    def __init__(self, agent, job_id, name, func, options, is_enable, args, kwargs):
        if Job.logger is None:
            agent.get_logger()
        self._logger = agent.logger
        self._logger.info(f'initializing job {name}')
        self._id = job_id
        self._name = name
        self._agent = agent
        self.status = {
            'job_id': self._id,
            'name': self._name,
            'LastRunState': LastRuntimeState.never_executed,
            'LastRuntime': None

        }
        self.options = options
        self._func = func
        self.next_run_time = None
        self._calculate_next_run_time = Cnrt(self, options)
        self._job_fail_handler = JobFailHandler(self, options=options)
        self.next_run_time = self._calculate_next_run_time()
        self.is_running = Event()
        self.is_enable = is_enable
        self.job_thread = threading.Thread()
        self._args = args

        func_sig = signature(self._func)
        if kwargs is None:
            kwargs = {}
        if (len(args) + len(kwargs) < len(func_sig.parameters)) and func_sig.parameters.get('agent') is not None:
            kwargs = {**kwargs, **{'agent': agent}}
        self._kwargs = kwargs
        self._initialized = True
        self._logger.info(f'job {name} has initialized')

    def _job_run(self):
        try:
            self._logger.info(f'starting job {self._name}')
            self._calculate_next_run_time()
            self.is_running.set()
            self._logger.info(f'executing job {self._name} function')
            self.status['last_return'] = self._func(*self._args, **self._kwargs)
            self.is_running.clear()
        except Exception as E:
            print(E)
            self.status['LastRunState'] = LastRuntimeState.failed
            self._job_fail_handler(exception=E)
            return 0
        else:
            self._logger.info(f'job {self._name} execute successfully')
            self.status['LastRunState'] = LastRuntimeState.success
        finally:
            self.status['LastRuntime'] = datetime.datetime.now()

    def stop(self, timeout: float = 10, silence_error=None):
        """
        stop job Thread if is is_running == True
        this function use threading join for stopping the Job Thread
        if is_running == False this function raise JobNotRunning but you can use silence_error

        if silence_error Not None than return  silence_error
        :param timeout: wait before kill job Thread by default is set to 10
        :param silence_error: None for raise JobNotRunning() or return silence_error if not none
        :return: 1 if successful None if not
        """
        if self.is_running:
            self.job_thread.join(timeout=timeout)
            return 1
        else:
            if silence_error:
                return None
            raise JobNotRunning()

    def start(self):
        """
        start job in a another Thread whit name of job
        by default daemon is set to True you can change this in options
        :return: 1 if successful
        """
        self.job_thread = Thread(target=self._job_run, daemon=self.options.get('daemon', True), name=self._name)
        self.job_thread.start()
        return 1

    @property
    def name(self):
        assert self._initialized, "job.__init__() not called"
        return self._name

    @name.setter
    def name(self, val):
        if not self._initialized:
            raise RuntimeError("Agent.__init__() not called")

        if self.is_running.is_set():
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
