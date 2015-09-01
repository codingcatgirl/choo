#!/usr/bin/env python3
from .base import Serializable
from datetime import datetime, timedelta
from . import fields


class RealtimeTime(Serializable):
    time = fields.DateTime(none=False)
    delay = fields.Timedelta()

    def __init__(self, time=None, delay=None, livetime=None, **kwargs):
        if livetime is not None:
            if time is None:
                time = livetime - delay
            elif delay is None:
                delay = livetime - time
            else:
                assert livetime - time == delay

        super().__init__(time=time, delay=delay, **kwargs)

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
        if isinstance(other, datetime):
            return self.livetime == other
        elif isinstance(other, RealtimeTime):
            return self.time == other.time
        return False

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
