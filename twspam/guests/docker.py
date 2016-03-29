import subprocess

from . import Guest, GuestError
from .. import network
from ..config import Config
from ..logger import Logger
from ..sudo import asuser


__all__ = (
    'DockerContainer',
)


config = Config(__name__)
logger = Logger(__name__)


class DockerContainer(Guest):

    def __init__(self, name):
        self.name = name
        self.interface = None

    def _docker_command(self, arguments):
        return asuser(config.docker_user, [config.docker_path] + arguments)

    def start(self):
        logger.info("Start container {}", self.name)
        interfaces = set(network.interfaces())
        command = self._docker_command(['start', self.name])
        subprocess.check_output(command)
        interfaces = set(network.interfaces()) - interfaces
        if len(interfaces) != 1:
            self.stop()
            raise GuestError("can't find network interface for container {}",
                             self.name)
        self.interface = interfaces.pop()
        logger.debug("Interface for container {} is {}",
                     self.name, self.interface)

    def stop(self):
        logger.info("Stop container {}", self.name)
        command = self._docker_command(['stop', self.name])
        subprocess.check_output(command)
        self.interface = None

    def kill(self):
        logger.info("Kill container {}", self.name)
        command = self._docker_command(['kill', self.name])
        subprocess.check_output(command)
        self.interface = None
