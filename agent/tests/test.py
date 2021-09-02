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
# Name: test.py
# Description: test the functionality of agent and job and other part of package
# Version: 0.0.6
# Author: Mohammad Reza Golsorkhi
# ------------------------------------------------------------------------------


import datetime
import time
from unittest import TestCase

from agent.agent import Agent


def test_func(t):
    print('I am running')
    c = t[0]
    t.append('in test func {}'.format(str(c)))
    t[0] += 1
    print(t)


def test_func_list_int_str(t):
    c = t[0] + 1
    t[0] = c
    t[1] = str(c)
    time.sleep(2)


class TestAgent(TestCase):
    options = {
        'scheduler': 'interval',
        'start_time': datetime.datetime.now(),
        'interval': 1
    }

    def test_run_job_by_id_and_name(self):
        agent = Agent()
        t = [0, '0']
        agent.create_job(func=test_func_list_int_str, options=TestAgent.options, args=(t,), name='norm1')

        @agent.create_job_decorator(options=TestAgent.options, args=(t,), name='dec1')
        def test_func_list_int_str_inner_and_job_is_running(t):
            c = t[0] + 1
            t[0] = c
            t[1] = str(c)
            time.sleep(2)

        agent.run_job_by_name('norm1')
        time.sleep(2.1)
        self.assertEqual([1, '1'], t)

        agent.run_job_by_id(2)
        time.sleep(2)
        self.assertEqual([2, '2'], t)
        self.assertEqual(0, agent.run_job_by_id(3))
        self.assertEqual(0, agent.run_job_by_name('asx'))
        self.assertEqual(2, len(agent.get_all_jobs()))
        self.assertIsNone(agent.get_job_by_id(4))

    def test_agent(self):
        agent = Agent()
        t = [1]
        print('job_id IS ' + str(id(t)))
        agent.create_job(func=test_func, options=TestAgent.options, args=(t,))
        agent.start()
        print(t)
        time.sleep(1)
        # self.assertIn('in test func 1', t)
        agent.stop()

    def test_interrupt(self):
        agent = Agent()
        t = [0, '0']
        agent.create_job(func=test_func_list_int_str, options=TestAgent.options, args=(t,))
        agent.start()
        time.sleep(0.1)
        self.assertEqual([1, '1'], t)
        print(t)
        time.sleep(3)
        print(t)
        self.assertEqual([2, '2'], t)
        print(t)
        agent.stop()
        print(t)
        time.sleep(3)
        self.assertEqual([2, '2'], t)

    @staticmethod
    def custom_interval(interval, job):

        if job.next_run_time is None:
            try:
                r = job.options['start_time']
            except KeyError:
                raise KeyError('start_time not fond')
        else:
            r = job.next_run_time + datetime.timedelta(seconds=interval)
        print('this is custom interval returning {}'.format(str(r)))
        return r

    def test_custom_CNRT(self):
        _options = {
            'scheduler': 'custom',
            'start_time': datetime.datetime.now(),
            'custom_time_scheduler': self.custom_interval,
            'args': (1,)
        }
        agent = Agent()
        t = [0, '0']
        agent.create_job(func=test_func_list_int_str, options=_options, args=(t,))
        agent.start()
        time.sleep(0.1)
        self.assertEqual([1, '1'], t)
        print(t)
        time.sleep(3)
        print(t)
        self.assertEqual([2, '2'], t)
        print(t)
        agent.stop()
        print(t)
        time.sleep(3)
        self.assertEqual([2, '2'], t)

    def test_job_return(self):
        agent = Agent()

        @agent.create_job_decorator(options=TestAgent.options, name='job_1')
        def test_func_list_int_str_inner_and_job_is_running():
            time.sleep(1)
            return 5

        agent.start()
        job = agent.get_job_by_name('job_1')
        self.assertIsNone(job.status.get('last_return'))
        time.sleep(2)
        print(job.status.get('last_return'))
        self.assertEqual(job.status.get('last_return'), 5)

    def test_job_fail_handler(self):
        def jfh(exception, job):
            job.status['jfh'] = 'Test'
            job.status['exception'] = exception

        options = {
            'scheduler': 'interval',
            'start_time': datetime.datetime.now(),
            'interval': 1,
            'job_fail_handler': {
                'Handler': 'custom',
                'custom_job_fail_Handler': jfh
            }
        }
        agent = Agent()

        @agent.create_job_decorator(options=options, name='job_1')
        def test_func_list_int_str_inner_and_job_is_running():
            time.sleep(1)
            raise Exception('test_exception')

        agent.start()
        job = agent.get_job_by_name('job_1')
        self.assertIsNone(job.status.get('jfh'))
        time.sleep(2)
        print(job.status.get('last_return'))
        self.assertEqual(job.status.get('jfh'), 'Test')

    def test_job_stop(self):

        agent = Agent()

        @agent.create_job_decorator(options=self.options, name='job_1')
        def test_func_list_int_str_inner_and_job_is_running():
            time.sleep(100)
            return 10

        job = agent.get_job_by_name('job_1')
        time.sleep(0.5)
        job.start()
        time.sleep(0.5)
        job.stop(2)
        time.sleep(2.5)
        print(job.status)
        self.assertIsNone(job.status.get('last_return'))
# TestAgent.test_job_fail_handler(TestAgent)
