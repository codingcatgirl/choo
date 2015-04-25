#!/usr/bin/env python3
from .base import ModelBase
from .location import Stop
from .realtimetime import RealtimeTime

class TimeAndPlace(ModelBase):
    def __init__(self, stop: Stop=None, platform: str=None, arrival: RealtimeTime=None, departure: RealtimeTime=None, coords: tuple=None):
        super().__init__()
        self.stop = stop
        self.platform = platform
        self.coords = coords
        self.arrival = arrival
        self.departure = departure

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'stop')
        self._serial_get(data, 'platform')
        self._serial_get(data, 'coords')
        self._serial_get(data, 'arrival')
        self._serial_get(data, 'departure')

    def __eq__(self, other):
        return (isinstance(other, TimeAndPlace) and self.stop == other.stop and
                self.platform == other.platform and self.arrival == other.arrival and
                self.departure == other.departure)

    def __repr__(self):
        return '<TimeAndPlace %s %s %s %s>' % (repr(self.arrival), repr(self.departure), repr(self.stop), repr(self.platform))

    def _serialize(self, ids):
        data = super()._serialize(ids)
        self._serial_add(data, 'stop', ids)
        self._serial_add(data, 'platform', ids)
        self._serial_add(data, 'coords', ids)
        self._serial_add(data, 'arrival', ids)
        self._serial_add(data, 'departure', ids)
        return data
