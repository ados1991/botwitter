from abc import ABC, abstractmethod

from .. import retry


class RemoteControllerError(Exception):
    pass


class RemoteController(ABC):

    default_timeout = 30.
    default_delay = 1.

    @abstractmethod
    def get_region(self, position, size):
        pass

    def check_region(self, region, maxrms=None):
        capture = self.get_region(region.position, region.size)
        if maxrms is None:
            return region == capture
        else:
            return region.similar(capture, maxrms=maxrms)

    def wait_region(self, region, maxrms=None, *, timeout=None, delay=None):
        if timeout is None:
            timeout = self.default_timeout
        if delay is None:
            delay = self.default_delay
        for _ in retry.until_timeout(timeout, delay):
            if self.check_region(region, maxrms):
                return

    @abstractmethod
    def type(self, message):
        pass

    @abstractmethod
    def keystroke(self, key):
        pass

    @abstractmethod
    def move(self, position):
        pass

    @abstractmethod
    def click(self, position, button=1):
        pass
