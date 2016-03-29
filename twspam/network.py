import re
import subprocess
import time

from contextlib import contextmanager
from enum import IntEnum

from . import retry
from .config import Config
from .logger import Logger


__all__ = (
    'interfaces',
    'CaptureError',
    'capturing',
    'Port',
)


config = Config(__name__)
logger = Logger(__name__)


_IFCONFIG_INTERFACE_RE = re.compile(r'^(?P<iface>\w+):?\s.*$')


def _iterinterfaces(attempts=2, delay=1.):
    command = [config.ifconfig_path, '-a']
    for _ in retry.n_times(attempts, delay):
        try:
            output = subprocess.check_output(command)
            break
        except subprocess.CalledProcessError:
            logger.error("Could not call {!r}, retry")
    for line in output.decode().splitlines():
        match = _IFCONFIG_INTERFACE_RE.match(line)
        if match is None:
            continue
        else:
            yield match.group('iface')


def interfaces(attempts=2, delay=1.):
    return list(_iterinterfaces(attempts, delay))


def _tcpdump_command(interfaces, pcap_path, *, ips=None, ports=None):
    filter_args = []
    if ips is not None:
        if len(ips) == 1:
            ip_filter = 'net {}'.format(ips[0])
        else:
            ip_filters = ('net {}'.format(ip) for ip in ips)
            ip_filter = '({})'.format(' or '.join(ip_filters))
        filter_args.append(ip_filter)
    if ports is not None:
        if len(ports) == 1:
            port_filter = 'port {}'.format(ports[0])
        else:
            port_filters = ('port {}'.format(port) for port in ports)
            port_filter = '({})'.format(' or '.join(port_filters))
        filter_args.append(port_filter)
    filter_arg = ' and '.join(filter_args)
    command = [config.tcpdump_path, '-q', '-n', '-s', '0']
    for interface in interfaces:
        command.extend(['-i', interface])
    command.extend(['-w', pcap_path, filter_arg])
    return command


class CaptureError(Exception):
    pass


@contextmanager
def capturing(interfaces, pcap_path, *, ips=None, ports=None):
    command = _tcpdump_command(interfaces, pcap_path, ips=ips, ports=ports)
    proc = subprocess.Popen(command)
    time.sleep(1)  # if tcpdump fails at start, we want to detect it
    proc.poll()
    if proc.returncode is not None:
        raise CaptureError("tcpdump failed with return code {}"
                           "".format(proc.returncode))
    try:
        yield
    finally:
        proc.terminate()


class Port(IntEnum):
    http = 80
    https = 443
