#!/usr/bin/env python3
from .base import Updateable
from datetime import datetime, timedelta


class RealtimeTime(Updateable):
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

    def __repr__(self):
        return '<RealtimeTime %s>' % (str(self))

    def __str__(self):
        out = self.time.strftime('%Y-%m-%d %H:%M')
        if self.delay is not None:
            out += ' %+d' % (self.delay.total_seconds() / 60)
        return out

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
        return RealtimeTime(self.time + other, self.delay)

    def __sub__(self, other):
        assert isinstance(other, timedelta)
        return RealtimeTime(self.time - other, self.delay)

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
