import time

from .logger import Logger


__all__ = (
    'RetryError',
    'n_times',
    'until_timeout',
)


logger = Logger(__name__)


class RetryError(Exception):
    pass


def n_times(attempts, delay=None):
    i = 0
    yield i
    while True:
        i += 1
        if i == attempts:
            raise RetryError("too many attempts")
        if delay is not None:
            time.sleep(delay)
        logger.debug("Retry for the {}-th time", i)
        yield i


def until_timeout(timeout, delay=None):
    i = 0
    yield i
    start_time = time.time()
    max_time = timeout
    if delay is not None:
        max_time -= delay
    while True:
        i += 1
        if time.time() - start_time > max_time:
            raise RetryError("timeout expired")
        if delay is not None:
            time.sleep(delay)
        logger.debug("Retry for the {}-th time", i)
        yield i
