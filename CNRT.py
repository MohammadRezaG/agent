import datetime
from inspect import signature

from exceptions import InvalidOption


def get_cnrt_func(job, option):
    if option.get('calculator'):
        return Cnrt(job, option)
    else:
        raise InvalidOption()


class Cnrt:
    def __init__(self, job, options):
        self.job = job
        self.options = options

        if self.options.get('calculator') == 'interval':
            self.func = self._interval
        elif self.options.get('calculator') == 'custom':
            self.func = self._custom
        else:
            raise InvalidOption()

    def __call__(self, *args, **kwargs):
        return self.func()

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
                self._custom_func_sig = func_sig = signature(self._custom_func)
                self._custom_func_args = self.options.get('args', ())
                self._custom_func_kwargs = self.options.get('kwargs', {})
                if (len(self._custom_func_args) + len(self._custom_func_kwargs) < len(
                        func_sig.parameters)) and func_sig.parameters.get('job') is not None:
                    self._custom_func_kwargs = {
                        **self._custom_func_kwargs, **{'job': self.job}}

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
