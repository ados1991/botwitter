import random
import shutil
import time

from abc import ABC, abstractmethod
from os.path import exists, join
from tempfile import TemporaryDirectory

from .config import Config
from .logger import Logger
from .sudo import fixperms


__all__ = (
    'ApplicationError',
    'Application',
)


config = Config(__name__)
logger = Logger(__name__)


class ApplicationError(Exception):
    pass


class Application(ABC):

    def __init__(self, controller, region_loader, session_info):
        self.controller = controller
        self.regions = region_loader.getregions()
        self.session_info = session_info

    @abstractmethod
    def capturing(self, tempdir):
        pass

    @abstractmethod
    def session(self):
        pass

    def run(self, output_dir):
        if exists(output_dir):
            raise RuntimeError("directory {!r} exists".format(output_dir))
        with TemporaryDirectory(prefix=config.tempdir_prefix) as tempdir:
            with self.capturing(tempdir):
                self.session()
            session_info_filepath = join(tempdir, config.session_info_filename)
            with open(session_info_filepath, 'w') as session_info_fileobj:
                self.session_info.dump_json(session_info_fileobj)
            shutil.copytree(tempdir, output_dir)
        # XXX perhaps something better could be achieved with os.set*id
        fixperms(output_dir, config.session_user, config.session_group,
                 config.session_umask)


def gaussian_sleep(mu, sigma):
    while True:
        delay = random.gauss(mu, sigma)
        if delay > 0:
            break
    time.sleep(delay)
