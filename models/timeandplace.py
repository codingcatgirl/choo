#!/usr/bin/env python3
from .base import ModelBase
from .locations import Platform
from .realtime import RealtimeTime


class TimeAndPlace(ModelBase):
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

    def _serialize(self, depth):
        data = {}
        data['platform'] = self.platform.serialize()
        if self.arrival:
            data['arrival'] = self.arrival.serialize()
        if self.departure:
            data['departure'] = self.departure.serialize()
        data['passthrough'] = self.passthrough
        return data

    def _unserialize(self, data):
        self.platform = Platform.unserialize(data['platform'])
        if 'arrival' in data:
            self.arrival = RealtimeTime.unserialize(data['arrival'])
        if 'departure' in data:
            self.departure = RealtimeTime.unserialize(data['departure'])
        if 'passthrough' in data:
            self.passthrough = data['passthrough']

    @property
    def stop(self):
        return self.platform.stop

    def __eq__(self, other):
        assert isinstance(other, TimeAndPlace)
        return (self.platform == other.platform and
                self.arrival == other.arrival and
                self.departure == other.departure)

    def __repr__(self):
        return ('<TimeAndPlace %s %s %s>' %
                (self.arrival, self.departure, self.platform))
