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
# Name: handler.py
# Description: contain necessary Handler for job
# Version: 0.1.0
# Author: Mohammad Reza Golsorkhi
# ------------------------------------------------------------------------------


import datetime
import logging
from inspect import signature

from agent.exceptions import InvalidOption


class _BaseHandler:
    """
    BaseHandler is a Interface do not use it
    """

    def __init__(self, job, options):
        """

        :param job:
        :param options:
        """
        self.func = None
        self.job = job
        self.options = options

    def __call__(self, *args, **kwargs):
        return self.func()

    def _custom_func_get_args_and_kwargs(self, func, pass_args: dict):
        """
        this function return a tuple of args And kwargs
        use this function is not recommended for use outside of handler
        please read the src of handler.py for better understanding of how this function works
        :param func: function for checking signature
        :param pass_args: name of args that if user want send to function
        :return: (args, kwargs)
        """
        func_sig = signature(func)
        custom_func_args = self.options.get('args', ())
        custom_func_kwargs = self.options.get('kwargs', {})
        for args_name in pass_args:
            if (len(custom_func_args) + len(custom_func_kwargs) < len(
                    func_sig.parameters)) and func_sig.parameters.get(args_name) is not None:
                custom_func_kwargs = {
                    **custom_func_kwargs, **{args_name: pass_args[args_name]}}

        return custom_func_args, custom_func_kwargs


class Cnrt(_BaseHandler):
    """
    Cnrt stands for calculate_next_run_time
    it is inherited from BaseHandler but dose not call _BaseHandler __init__
    """

    def __init__(self, job, options):
        self.job = job
        self.options = options

        if self.options.get('calculator') == 'interval':
            self.func = self._interval
        elif self.options.get('calculator') == 'custom':
            self.func = self._custom
        else:
            raise InvalidOption()

    def _interval(self):
        if self.options.get('interval'):
            if self.job.next_run_time is None:
                try:
                    return self.options['start_time']
                except KeyError:
                    raise InvalidOption('start_time not fond')
            else:
                return self.job.next_run_time + datetime.timedelta(seconds=self.options['interval'])
        else:
            raise InvalidOption('interval not fond')

    def _custom(self):

        if not hasattr(self, '_custom_func'):
            if self.options.get('custom_time_calculator'):
                self._custom_func = self.options['custom_time_calculator']
                self._custom_func_args, self._custom_func_kwargs = self._custom_func_get_args_and_kwargs(
                    self._custom_func, {'job': self.job})
            else:
                raise InvalidOption(
                    'must add custom_time_calculator whit your time calculator function that return datetime object')

        calculated_time = self._custom_func(*self._custom_func_args, **self._custom_func_kwargs)
        if isinstance(calculated_time, datetime.datetime):
            return calculated_time
        else:
            raise InvalidOption(
                'custom_time_calculator must return datetime object it return {}'.format(
                    str(type(calculated_time))))


class JobFailHandler(_BaseHandler):
    def __init__(self, job, options):
        super().__init__(job, options)
        self.fail_counter = 0
        if options.get('job_fail_handler'):
            self.job_fail_handler_options = options.get('job_fail_handler')
        else:
            self.job_fail_handler_options = {'Handler': 'basics'}

        if self.job_fail_handler_options.get('Handler') == 'basics':
            self.func = self._basics
        elif self.job_fail_handler_options.get('Handler') == 'rerun':
            self.func = self._rerun
        elif self.job_fail_handler_options.get('Handler') == 'custom':
            self.func = self._custom
        else:
            raise InvalidOption()

    def __call__(self, *args, **kwargs):
        self.func(kwargs.get('exception', Exception('unknown Error')))

    def _basics(self, exception: Exception):
        logging.log(level=logging.CRITICAL, msg=f'job: {self.job.name} Failed to Execute du \n {exception}',
                    exc_info=True)

    def _rerun(self, exception: Exception):
        pass

    def _custom(self, exception: Exception):

        if not hasattr(self, '_custom_func'):
            if self.job_fail_handler_options.get('custom_job_fail_Handler'):
                self._custom_func = self.job_fail_handler_options['custom_job_fail_Handler']
                self._custom_func_args, self._custom_func_kwargs = self._custom_func_get_args_and_kwargs(
                    self._custom_func, {'exception': exception, 'job': self.job})
            else:
                raise InvalidOption(
                    'must add custom_job_fail_Handler whit your time job_fail function ')

        self._custom_func(*self._custom_func_args, **self._custom_func_kwargs)
