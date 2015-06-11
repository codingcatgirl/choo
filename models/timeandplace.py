#!/usr/bin/env python3
from .base import Updateable
from .locations import Platform
from .realtime import RealtimeTime


class TimeAndPlace(Updateable):
    def __init__(self, platform=None, arrival=None, departure=None):
        super().__init__()
        self.platform = platform
        self.arrival = arrival
        self.departure = departure
        self.passthrough = False

    @classmethod
    def _validate(cls):
        return {
            'platform': (None, Platform),
            'arrival': (None, RealtimeTime),
            'departure': (None, RealtimeTime),
            'passthrough': bool
        }

    @property
    def stop(self):
        return self.platform.stop

    def __eq__(self, other):
        assert isinstance(other, TimeAndPlace)
        return (self.platform == other.platform and
                self.arrival == other.arrival and
                self.departure == other.departure)

    def __repr__(self):
        return ('<TimeAndPlace %s %s %s>' % (self.arrival, self.departure, self.platform))
