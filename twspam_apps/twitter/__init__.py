import random

from abc import abstractmethod

from faker import Faker

from twspam.apps import Application, ApplicationError, gaussian_sleep
from twspam.config import Config
from twspam.logger import Logger


__all__ = (
    'TwitterError',
    'TwitterApp',
)


config = Config(__name__)
logger = Logger(__name__)


class TwitterError(ApplicationError):
    pass


class TwitterApp(Application):

    def __init__(self, controller, region_loader, trace_info):
        super().__init__(controller, region_loader, trace_info)
        self._fake = Faker()

    @abstractmethod
    def open_browser(self):
        pass

    @abstractmethod
    def close_browser(self):
        pass

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def tweet(self, message):
        pass

    def session(self):
        num_tweets = random.randint(config.min_tweets, config.max_tweets)
        logger.info("Start Twitter session, {} tweets", num_tweets)
        try:
            logger.debug("Open browser")
            self.open_browser()
            logger.debug("Accept cookies")
            self.accept_cookies()
            logger.debug("Log in")
            self.login()
            for i in range(num_tweets):
                gaussian_sleep(config.sleep_mu, config.sleep_sigma)
                logger.debug("Send tweet")
                self.tweet(self._fake.text(140))
            gaussian_sleep(config.sleep_mu, config.sleep_sigma)
            logger.debug("Log out")
            self.logout()
            logger.debug("Close browser")
            self.close_browser()
        finally:
            logger.info("Stop Twitter session")
