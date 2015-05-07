#!/usr/bin/env python3
from .base import ModelBase
from .locations import Coordinates, Stop
from .realtime import RealtimeTime


class Platform(ModelBase):
    def __init__(self, stop=None, name=None):
        super().__init__()
        self.stop = stop
        self.name = name

    @classmethod
    def _validate(cls):
        return {
            'stop': (None, Stop),
            'name': str
        }

    def _serialize(self, depth):
        data = {}
        data['name'] = self.name
        return data

    def _unserialize(self, data):
        self.name = data['name']

    def __repr__(self, data):
        return '<Platform %s>' % self.name


class TimeAndPlace(ModelBase):
    def __init__(self, stop=None, platform=None, arrival=None, departure=None, coords=None):
        super().__init__()
        self.stop = stop
        self.platform = platform
        self.coords = coords
        self.arrival = arrival
        self.departure = departure

    @classmethod
    def _validate(cls):
        return {
            'platform': (None, Platform),
            'coords': (None, Coordinates),
            'arrival': (None, RealtimeTime),
            'departure': (None, RealtimeTime)
        }

    def _serialize(self, depth):
        data = {}
        data['stop'] = self.stop.serialize(depth)
        if self.platform:
            data['platform'] = self.platform.serialize()
        if self.coords:
            data['coords'] = self.coords.serialize()
        if self.arrival:
            data['arrival'] = self.arrival.serialize()
        if self.departure:
            data['departure'] = self.departure.serialize()
        return data

    def _unserialize(self, data):
        self._serial_get(data, 'platform')
        self.stop = Stop.unserialize(data['stop'])
        if 'coords' in data:
            self.coords = Coordinates.unserialize(data['coords'])
        if 'arrival' in data:
            self.arrival = RealtimeTime.unserialize(data['arrival'])
        if 'departure' in data:
            self.departure = RealtimeTime.unserialize(data['departure'])

    def __eq__(self, other):
        assert isinstance(other, TimeAndPlace)
        return (self.stop == other.stop and
                self.platform == other.platform and
                self.arrival == other.arrival and
                self.departure == other.departure)

    def __repr__(self):
        return ('<TimeAndPlace %s %s %s %s>' %
                (self.arrival, self.departure, repr(self.stop), self.platform))
