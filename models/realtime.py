#!/usr/bin/env python3
from .base import ModelBase, Serializable
from datetime import datetime, timedelta


class RealtimeTime(Serializable):
    _validate = {
        'time': datetime,
        'delay': (None, timedelta)
    }
    
    def __init__(self, time: datetime=None, delay: timedelta=None, livetime: datetime=None):
        super().__init__()
        if time is not None and livetime is not None:
            if delay is not None:
                assert livetime-time == delay
            else:
                delay = livetime-time

        self.time = time
        self.delay = delay
        
    def _serialize(self, depth):
        return [self.time.strftime('%Y-%m-%d %H:%M:%S'), self.delay.total_seconds() if self.delay is not None else None]
        
    def _unserialize(self, data):
        self.time = datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S')
        if data[1] is not None:
            self.delay = timedelta(seconds=data[1])

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
        