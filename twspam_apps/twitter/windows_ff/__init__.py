import os
import shutil
import time

from contextlib import contextmanager
from os.path import exists, join

from twspam import network
from twspam.config import Config
from twspam.controllers.vnc import VNCDoController
from twspam.guests.vbox import VBoxVM
from twspam.logger import Logger
from twspam.regions import RegionLoader
from twspam.sessions import SessionInfo

from .. import TwitterApp


config = Config(__name__)
main_config = Config('twspam')
logger = Logger(__name__)


class TwitterWindowsFirefoxVM(VBoxVM):

    def __init__(self):
        super().__init__(config.vm_name, config.vm_snapshot)
        self.interface = config.vm_interface

    def start(self):
        if exists(config.vm_sslkeys_filepath):
            os.remove(config.vm_sslkeys_filepath)
        super().start()
        time.sleep(config.vm_startup_time)


class TwitterWindowsFirefoxApp(TwitterApp):

    def __init__(self):
        controller = VNCDoController(config.vm_ip)
        regions = RegionLoader(config.regions_dirpath)
        session_info = SessionInfo(app='Twitter', os='Windows 7',
                                   guest='VirtualBox',
                                                     browser='Mozilla Firefox')
        super().__init__(controller, regions, session_info)
        self.vm = TwitterWindowsFirefoxVM()

    @contextmanager
    def capturing(self, tempdir):
        pcap_filepath = join(tempdir, main_config.session_pcap_filename)
        sslkeys_filepath = join(tempdir, main_config.session_sslkeys_filename)
        with self.vm.started():
            with network.capturing([self.vm.interface], pcap_filepath,
                                   ips=config.capture_ips,
                                   ports=config.capture_ports):
                yield
        shutil.copy(config.vm_sslkeys_filepath, sslkeys_filepath)

    def open_browser(self):
        self.controller.wait_region(self.regions.taskbar_nobrowser)
        self.controller.click((274, 745))
        self.controller.move((0, 0))
        self.controller.wait_region(self.regions.taskbar_firefox)
        self.controller.keystroke('ctrl-P')
        self.controller.wait_region(self.regions.firefox_incognitto)
        self.controller.type(config.twitter_start_page)
        self.controller.keystroke('enter')
        self.controller.wait_region(self.regions.passfield_cookies, timeout=60)

    def accept_cookies(self):
        self.controller.check_region(self.regions.cookiebtn)
        self.controller.click((903, 201))
        self.controller.wait_region(self.regions.passfield_nocookies)

    def login(self):
        self.controller.click((640, 211))
        self.controller.type(config.twitter_username)
        self.controller.keystroke('tab')
        self.controller.type(config.twitter_password)
        with self.session_info.adding_event('login'):
            self.controller.keystroke('enter')
            self.controller.wait_region(self.regions.tweetfield_collapsed)

    def tweet(self, message):
        self.controller.click((446, 152))
        self.controller.wait_region(self.regions.tweetbtn_disabled)
        self.controller.click((453, 156))
        self.controller.type(message)
        self.controller.wait_region(self.regions.tweetbtn_enabled)
        with self.session_info.adding_event('tweet'):
            self.controller.click((888, 262))
            self.controller.wait_region(self.regions.tweetfield_collapsed)

    def logout(self):
        self.controller.click((877, 94))
        self.controller.wait_region(self.regions.usermenu_expanded)
        with self.session_info.adding_event('logout'):
            self.controller.click((803, 394))
            self.controller.wait_region(self.regions.byelogo)

    def close_browser(self):
        self.controller.keystroke('alt-f4')
        self.controller.wait_region(self.regions.taskbar_firefox)
        self.controller.keystroke('alt-f4')
        self.controller.wait_region(self.regions.taskbar_nobrowser)
