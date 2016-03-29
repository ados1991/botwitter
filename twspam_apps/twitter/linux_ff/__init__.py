import os
import time
import shlex
import shutil

from contextlib import contextmanager
from os.path import exists, join

from twspam import network
from twspam.config import Config
from twspam.controllers.vnc import VNCDoController
from twspam.guests.docker import DockerContainer
from twspam.logger import Logger
from twspam.regions import RegionLoader
from twspam.sessions import SessionInfo

from .. import TwitterApp


__all__ = (
    'TwitterLinuxFirefoxApp',
)


config = Config(__name__)
main_config = Config('twspam')
logger = Logger(__name__)


class TwitterLinuxFirefoxContainer(DockerContainer):

    def __init__(self):
        super().__init__(config.container_name)

    def start(self):
        if exists(config.container_sslkeys_filepath):
            os.remove(config.container_sslkeys_filepath)
        super().start()
        time.sleep(config.container_startup_time)


class TwitterLinuxFirefoxApp(TwitterApp):

    def __init__(self):
        controller = VNCDoController()
        region_loader = RegionLoader(config.regions_dirpath)
        session_info = SessionInfo(app='Twitter', os='Ubuntu',
                                   guest='Docker', browser='Firefox')
        super().__init__(controller, region_loader, session_info)
        self.container = TwitterLinuxFirefoxContainer()

    @contextmanager
    def capturing(self, tempdir):
        pcap_filepath = join(tempdir, main_config.session_pcap_filename)
        sslkeys_filepath = join(tempdir, main_config.session_sslkeys_filename)
        with self.container.started():
            with network.capturing([self.container.interface], pcap_filepath,
                                   ips=config.capture_ips,
                                   ports=config.capture_ports):
                yield
        shutil.copy(config.container_sslkeys_filepath, sslkeys_filepath)

    def open_browser(self):
        self.controller.wait_region(self.regions.console)
        self.controller.click((1, 1))
        self.controller.keystroke('ctrl-c')
        self.controller.type('firefox -private {}'.format(
            shlex.quote(config.twitter_start_page)))
        self.controller.keystroke('enter')
        self.controller.wait_region(self.regions.passfield_cookies)

    def accept_cookies(self):
        self.controller.check_region(self.regions.cookiesbtn)
        self.controller.click((875, 215))
        self.controller.wait_region(self.regions.passfield_nocookies)

    def login(self):
        self.controller.click((615, 230))
        self.controller.type(config.twitter_username)
        self.controller.keystroke('tab')
        self.controller.type(config.twitter_password)
        with self.session_info.adding_event('login'):
            self.controller.keystroke('enter')
            self.controller.wait_region(self.regions.tweetfield_collapsed)

    def tweet(self, message):
        self.controller.click((410, 170))
        self.controller.wait_region(self.regions.tweetbtn_disabled)
        self.controller.type(message)
        self.controller.wait_region(self.regions.tweetbtn_enabled)
        with self.session_info.adding_event('tweet'):
            self.controller.click((850, 275))
            self.controller.wait_region(self.regions.tweetfield_collapsed)

    def logout(self):
        self.controller.click((850, 110))
        self.controller.wait_region(self.regions.usermenu_expanded)
        with self.session_info.adding_event('logout'):
            self.controller.click((770, 410))
            self.controller.wait_region(self.regions.byelogo)

    def close_browser(self):
        self.controller.click((0, 0))
        self.controller.keystroke('ctrl-q')
        self.controller.wait_region(self.regions.console)
