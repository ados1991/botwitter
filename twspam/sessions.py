import json
import time

from collections import namedtuple
from contextlib import contextmanager

from .config import Config
from .logger import Logger


config = Config(__name__)
logger = Logger(__name__)


__all__ = (
    'SessionInfo',
)


SessionEvent = namedtuple('SessionEvent', 'name start_ts stop_ts')


class SessionInfo:

    __slots__ = (
        'app',
        'os',
        'guest',
        'browser',
        'events',
    )

    def __init__(self, *, app, os, guest, browser):
        self.app = app
        self.os = os
        self.guest = guest
        self.browser = browser
        self.events = []

    def add_event(self, name, start_ts, stop_ts):
        logger.info("Add event {!r}", name)
        event = SessionEvent(name, start_ts, stop_ts)
        self.events.append(event)

    @contextmanager
    def adding_event(self, name):
        start_ts = time.time()
        yield
        stop_ts = time.time()
        self.add_event(name, start_ts, stop_ts)

    def _asdict(self):
        data = {'app': self.app, 'os': self.os, 'guest': self.guest,
                'browser': self.browser}
        data['events'] = [event._asdict() for event in self.events]
        return data

    def dump_json(self, fileobj):
        data = self._asdict()
        json.dump(data, fileobj, indent=4, sort_keys=True)

    @classmethod
    def load_json(cls, fileobj):
        data = json.load(fileobj)
        events = [SessionEvent(**datum) for datum in data['events']]
        del data['events']
        info = SessionInfo(**data)
        info.events = events
        return info
