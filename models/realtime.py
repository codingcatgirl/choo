#!/usr/bin/env python3
from .base import Serializable
from datetime import datetime, timedelta


class RealtimeTime(Serializable):
    def __init__(self, time=None, delay=None, livetime=None):
        super().__init__()
        if time is not None and livetime is not None:
            if delay is not None:
                assert livetime - time == delay
            else:
                delay = livetime - time

        self.time = time
        self.delay = delay

    @classmethod
    def _validate(cls):
        return {
            'time': datetime,
            'delay': (None, timedelta)
        }

    def _serialize(self, depth):
        return [self.time.strftime('%Y-%m-%d %H:%M:%S'),
                int(self.delay.total_seconds()) if self.delay is not None else None]

    def _unserialize(self, data):
        self.time = datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S')
        if data[1] is not None:
            self.delay = timedelta(seconds=data[1])

    def __repr__(self):
        delay = ''
        if self.delay is not None:
            delay = ' +%d' % (self.delay.total_seconds() / 60)
        return '<RealtimeTime %s%s>' % (str(self.time), delay)

    @property
    def is_live(self):
        return self.delay is not None

    @property
    def livetime(self):
        if self.delay is not None:
            return self.time + self.delay
        else:
            return self.time

    def __add__(self, other):
        assert isinstance(other, timedelta)
        return RealtimeTime(self.time+other, self.delay)

    def __sub__(self, other):
        assert isinstance(other, timedelta)
        return RealtimeTime(self.time-other, self.delay)

    def __eq__(self, other):
        assert isinstance(other, RealtimeTime) or isinstance(other, datetime)
        if isinstance(other, datetime):
            return self.livetime == other
        else:
            return self.livetime == other.livetime

    def __lt__(self, other):
        assert isinstance(other, RealtimeTime) or isinstance(other, datetime)
        if isinstance(other, datetime):
            return self.livetime < other
        else:
            return self.livetime < other.livetime

    def __gt__(self, other):
        assert isinstance(other, RealtimeTime) or isinstance(other, datetime)
        if isinstance(other, datetime):
            return self.livetime < other
        else:
            return self.livetime < other.livetime
