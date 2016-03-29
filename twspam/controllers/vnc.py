import subprocess

from os.path import join
from tempfile import TemporaryDirectory

from . import RemoteController
from .. import regions
from .. import retry
from ..config import Config
from ..logger import Logger


config = Config(__name__)
logger = Logger(__name__)


class VNCController(RemoteController):

    def __init__(self, server=None, *, port=None, password=None, display=None):
        self.server = server
        self.port = port
        self.password = password
        self.display = display


class VNCDoController(VNCController):

    def __init__(self, server=None, *, port=None, password=None, display=None):
        super().__init__(server, port=port, password=password, display=display)
        self._vncdo_prefix = [config.vncdo_path]
        if server is not None:
            host_arg = str(server)
            if display is not None:
                host_arg += ':{}'.format(display)
            if port is not None:
                host_arg += '::{}'.format(port)
            self._vncdo_prefix.extend(['-s', host_arg])
        if password is not None:
            self._vncdo_prefix.extend(['-p', password])

    def _vncdo_command(self, arguments):
        return self._vncdo_prefix + arguments

    def _vncdo(self, arguments, *, attempts=1, timeout=None, delay=1.):
        # sometimes the command hangs, hence this setup
        command = self._vncdo_command(arguments)
        for _ in retry.n_times(attempts, delay):
            try:
                subprocess.check_call(command, timeout=timeout)
                return
            except subprocess.TimeoutExpired:
                logger.warning("Timeout expired for vncdo command, retry")

    def get_region(self, position, size):
        filename = 'out.png'
        with TemporaryDirectory(prefix=config.tempdir_prefix) \
                as dirpath:
            filepath = join(dirpath, filename)
            arguments = ['rcapture', filepath,
                         str(position[0]), str(position[1]),
                         str(size[0]), str(size[1])]
            self._vncdo(arguments)
            return regions.Region(filepath, position)

    def type(self, message):
        arguments = ['type', message]
        self._vncdo(arguments)

    def keystroke(self, key):
        arguments = ['key', key]
        self._vncdo(arguments)

    def move(self, position):
        arguments = ['move', str(position[0]), str(position[1])]
        self._vncdo(arguments)

    def click(self, position, button=1):
        arguments = ['move', str(position[0]), str(position[1]),
                     'click', str(button)]
        self._vncdo(arguments)
