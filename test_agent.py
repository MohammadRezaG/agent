from unittest import TestCase
from agent import Agent
import datetime
import time


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
        'calculator': 'interval',
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
            'calculator': 'custom',
            'start_time': datetime.datetime.now(),
            'custom_time_calculator': self.custom_interval,
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
            time.sleep(4)
            return 5

        agent.start()
        job = agent.get_job_by_name('job_1')
        self.assertIsNone(job.status.get('last_return'))
        time.sleep(4)
        print(job.status.get('last_return'))
        self.assertEqual(job.status.get('last_return'),5)
# TestAgent.test_custom_CNRT(TestAgent)
