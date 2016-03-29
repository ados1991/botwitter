from abc import ABC, abstractmethod
from contextlib import contextmanager


class GuestError(Exception):
    pass


class Guest(ABC):

    @abstractmethod
    def start(self):
        pass

    def stop(self):
        self.kill()

    @abstractmethod
    def kill(self):
        pass

    @contextmanager
    def started(self):
        value = self.start()
        try:
            yield value
        finally:
            self.stop()
