import threading

from threading import Thread, Event
import datetime
from inspect import signature
from enum import Enum
from CNRT import get_cnrt_func
from exceptions import DuplicateName


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
        self._calculate_next_run_time = get_cnrt_func(self, options)
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
            self._func(*self._args, **self._kwargs)
            self.is_running.clear()
        except Exception as E:
            print(E)
            self.status['LastRunState'] = LastRuntimeState.failed
            self._logger.info(f'job {self._name} failed', exc_info=True)
            return 0
        else:
            self._logger.info(f'job {self._name} execute successfully')
            self.status['LastRunState'] = LastRuntimeState.success
        finally:
            self.status['LastRuntime'] = datetime.datetime.now()

    def stop(self):
        if self.is_running:
            self.job_thread.join(10)
        else:
            raise DuplicateName()

    def start(self):
        self.job_thread = Thread(target=self._job_run, daemon=self.options.get('daemon', True), name=self._name)
        self.job_thread.start()

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
    def initialized(self):
        assert self._initialized, "job.__init__() not called"
        return self._initialized

    @initialized.setter
    def initialized(self, val):
        raise PermissionError('Do not change job.initialized')
