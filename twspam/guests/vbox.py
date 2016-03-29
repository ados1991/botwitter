import subprocess

from . import Guest, GuestError
from ..config import Config
from ..logger import Logger
from ..sudo import asuser


__all__ = (
    'VBoxError',
    'VBoxVM',
)


config = Config(__name__)
logger = Logger(__name__)


class VBoxError(GuestError):
    pass


class VBoxVM(Guest):

    def __init__(self, vm_name, snapshot_name):
        self.vm_name = vm_name
        self.snapshot_name = snapshot_name

    def _vbox_command(self, arguments):
        return asuser(config.vboxmanage_user,
                      [config.vboxmanage_path] + arguments)

    def _check_snapshot(self):
        command = self._vbox_command([
            'showvminfo', self.vm_name, '--machinereadable'])
        output = subprocess.check_output(command)
        for line in output.splitlines():
            if line == 'SnapshotName="{}"'.format(self.snapshot_name):
                break
        else:
            raise VBoxError("can't find snapshot {!r}"
                            "".format(self.snapshot_name))

    def _restore_snapshot(self):
        logger.debug("Restore snapshot {!r} of VM {!r}",
                     self.snapshot_name, self.vm_name)
        command = self._vbox_command([
            'snapshot', self.vm_name, 'restore', self.snapshot_name])
        subprocess.check_call(command)

    def start(self):
        logger.info("Start VM {!r}", self.vm_name)
        self._restore_snapshot()
        subprocess.check_call(self._vbox_command(['startvm', self.vm_name]))

    def kill(self):
        logger.info("Stop VirtualBox VM {}", self.vm_name)
        command = self._vbox_command(['controlvm', self.vm_name, 'poweroff'])
        subprocess.check_call(command)
