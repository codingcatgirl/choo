#!/usr/bin/env python3
from .base import ModelBase
from datetime import datetime, timedelta

class RealtimeTime(ModelBase):
    def __init__(self, time: datetime, delay: timedelta=None, livetime: datetime=None):
        super().__init__()
        if livetime is not None:
            if delay is not None:
                assert livetime-time == delay
            else:
                delay = livetime-time

        self.time = time
        self.delay = delay

    @classmethod
    def load(cls, data):
        time = ModelBase.unserialize(data.get('time', None))
        delay = ModelBase.unserialize(data.get('delay', None))
        livetime = ModelBase.unserialize(data.get('livetime', None))
        obj = cls(time, delay, livetime)
        obj._load(data)
        return obj

    def __repr__(self):
        return '<RealtimeTime %s%s>' % (str(self.time)[:-3], (' +%d' % (self.delay.total_seconds()/60)) if self.delay is not None else '')

    @property
    def is_live(self):
        return self.delay is not None

    @property
    def livetime(self):
        if self.delay is not None:
            return self.time+self.delay
        else:
            return self.time

    def __add__(self, other):
        assert isinstance(other, timedelta)
        self.time += other

    def __sub__(self, other):
        assert isinstance(other, timedelta)
        self.time -= other

    def __eq__(self, other):
        return self.time == other.time

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, 'time', ids)
        self._serial_add(data, 'delay', ids)
        return data
