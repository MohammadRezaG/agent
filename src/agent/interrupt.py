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
# name: interrupt.py
# Description: contain necessary Handler for job and agent
# Version: 0.1.1
# Author: Mohammad Reza Golsorkhi
# ------------------------------------------------------------------------------
import logging
from threading import Event, Lock


class BaseInterrupt(Event):

    def __init__(self, agent):
        super().__init__()
        self._agent = agent
        self.lock = Lock()

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, val):
        raise PermissionError('cannot set Agent')

    # Deleter method
    @agent.deleter
    def agent(self):
        raise PermissionError('cannot delete agent')

    def interrupt_handler(self):
        """
        this function always run after Interrupt set by agent thread
        """
        print(24)


class StopInterrupt(BaseInterrupt):

    def interrupt_handler(self):
        logging.log(level=logging.INFO, msg=f'StopInterrupt interrupt_handler was run for agent {self.agent}')
        for job in self.agent.get_all_running_jobs():
            job.job_thread.join()


class RunJobNow(BaseInterrupt):
    def __init__(self, agent, job):
        super().__init__(agent)
        self.job = job

    def interrupt_handler(self):
        self.agent.run_job(self.job)

class NoneInterrupt(BaseInterrupt):
    """
    this Interrupt is for empty Interrupt
    and must only called in agent init phase
    """

    def interrupt_handler(self):
        pass
