import itertools
import re

from ipaddress import ip_network
from os.path import dirname, join

from .logger import Logger


__all__ = (
    'load_mapping',
)


logger = Logger(__name__)


_config_map = {}


def load_mapping(mapping):
    if hasattr(mapping, 'items'):
        items = mapping.items()
    else:
        items = mapping
    for module_name, entries in items:
        if module_name not in _config_map:
            _config_map[module_name] = {}
        _config_map[module_name] = entries


_SEPARATOR_RE = re.compile(r'(\.)')


class Config:

    def __init__(self, module_name):
        self._module_name = module_name
        components = _SEPARATOR_RE.split(module_name)
        paths = list(itertools.accumulate(components))
        paths.reverse()
        self._paths = paths

    def __getattribute__(self, name):
        logger.debug("Query {!r}.{}", self, name)
        paths = object.__getattribute__(self, '_paths')
        for path in paths:
            try:
                return _config_map[path][name]
            except:
                pass
        raise KeyError(name)

    def __repr__(self):
        module_name = object.__getattribute__(self, '_module_name')
        return 'Config({!r})'.format(module_name)


_user, _group = 'vivien:vivien'.split(':')
_project_path = dirname(dirname(__file__))
_assets_path = join(_project_path, 'assets')
_twitter_path = join(_project_path, 'twspam_apps/twitter')


load_mapping({
    'twspam': {
        'tempdir_prefix': 'twspam_',
        'session_user': _user,
        'session_group': _group,
        'session_umask': 0o22,
        'session_dirname_fmt': '%Y-%m-%d_%H%M%S',
        'session_pcap_filename': 'capture.pcap',
        'session_info_filename': 'info.json',
        'session_sslkeys_filename': 'sslkeylog.txt',
        'vncdo_path': 'vncdotool',
        'docker_path': 'docker',
        'docker_user': _user,
        'vboxmanage_path': 'VBoxManage',
        'vboxmanage_user': _user,
        'ifconfig_path': 'ifconfig',
        'tcpdump_path': 'tcpdump',
    },
    'twspam_apps.twitter': {
        'capture_ips': [ip_network('199.0.0.0/8')],
        'capture_ports': [80, 443],
        'twitter_start_page': 'https://twitter.com/?lang=en',
        'twitter_username': 'publicjohn01@laposte.net',
        'twitter_password': 'EAGLE2009',
        'tweet_max_len': 140,
        'min_tweets': 0,
        'max_tweets': 5,
        'sleep_mu': 60,
        'sleep_sigma': 15,
    },
    'twspam_apps.twitter.linux_ff': {
        'container_name': 'twspam-twitter-ff',
        'container_sslkeys_filepath': join(
            _assets_path, 'shares/twitter_linux_ff/sslkeylog.txt'),
        'container_startup_time': 10,
        'regions_dirpath': join(_twitter_path, 'linux_ff/regions'),
    },
    'twspam_apps.twitter.windows_cr': {
        'vm_name': 'twspam-windows',
        'vm_interface': 'enp0s25',
        'vm_snapshot': 'base-vnc-sslkeylog',
        'vm_ip': None,
        'vm_sslkeys_filepath': join(
            _assets_path, 'shares/twitter_windows/sslkeylog.txt'),
        'vm_startup_time': 10,
        'regions_dirpath': join(_twitter_path, 'windows_cr/regions'),
    },
    'twspam_apps.twitter.windows_ff': {
        'vm_name': 'twspam-windows',
        'vm_interface': 'enp0s25',
        'vm_snapshot': 'base-vnc-sslkeylog',
        'vm_ip': None,
        'vm_sslkeys_filepath': join(
            _assets_path, 'shares/twitter_windows/sslkeylog.txt'),
        'vm_startup_time': 10,
        'regions_dirpath': join(_twitter_path, 'windows_ff/regions'),
    },
})
