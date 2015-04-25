#!/usr/bin/env python3
from .base import ModelBase
from .location import Location

class Way(ModelBase):
    def __init__(self, origin: Location, destination: Location, distance: int=None):
        super().__init__()
        self.origin = origin
        self.destination = destination
        self.distance = None
        self.duration = None
        self.path = None
        # todo: self.stairs = None

    @classmethod
    def load(cls, data):
        origin = Location.unserialize(data['origin'])
        destination = Location.unserialize(data['destination'])
        obj = cls(origin, destination)
        obj.distance = data.get('distance', None)
        obj.duration = data.get('duration', None)
        obj.path = data.get('path', None)
        if obj.path:
            obj.path = [self.unserialize(p) for p in obj.path]
        return obj

    def __eq__(self, other):
        return (isinstance(other, Way) and self.origin == other.origin and self.destination == other.destination)

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, 'origin', ids)
        self._serial_add(data, 'destination', ids)
        self._serial_add(data, 'distance', ids)
        self._serial_add(data, 'duration', ids)
        if self.path:
            path = [('tuple', v) for v in self.path]
            self._serial_add(data, 'path', ids, val=path)
        return data
