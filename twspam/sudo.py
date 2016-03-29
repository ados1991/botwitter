import os
import shutil
import sys

from os.path import join


__all__ = (
    'asuser',
    'runasroot',
)


def asuser(user, command):
    if user is None:
        return command
    else:
        return ['sudo', '-u', user] + command


def runasroot():
    if os.geteuid() != 0:
        os.execvp('sudo', ['sudo'] + sys.argv)


def fixperms(dirpath, user=None, group=None, umask=22):
    for dirpath, dirnames, filenames in os.walk(dirpath):
        shutil.chown(dirpath, user, group)
        os.chmod(dirpath, 0o777 - umask)
        for filename in filenames:
            filepath = join(dirpath, filename)
            shutil.chown(filepath, user, group)
            os.chmod(filepath, 0o666 - umask)
