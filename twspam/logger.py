import itertools
import subprocess
import time

from functools import wraps

from logbook import Logger


__all__ = (
    'Logger',
)


def _monkey_patch(log_func, module, func_name):

    def tracelog(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            arg_strings = itertools.chain(
                ('{!r}'.format(arg) for arg in args),
                ('{}={!r}'.format(k, v) for k, v in kwargs.items()),
            )
            log_func("{}({})", func.__name__, ', '.join(arg_strings))
            return func(*args, **kwargs)
        return wrapper

    setattr(module, func_name, tracelog(getattr(module, func_name)))


_tracelog = Logger(__name__ + '.trace')

_monkey_patch(_tracelog.debug, subprocess, 'Popen')
_monkey_patch(_tracelog.debug, time, 'sleep')
