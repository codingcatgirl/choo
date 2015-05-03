#!/usr/bin/env python3
from .base import ModelBase
from .locations import Coordinates, Location, Stop, POI, Address
from datetime import timedelta


class Way(ModelBase):
    def __init__(self, origin=None, destination=None, distance=None):
        super().__init__()
        self.origin = origin
        self.destination = destination
        self.distance = None
        self.duration = None
        self.path = None

    @classmethod
    def _validate(cls):
        return {
            'origin': Location,
            'destination': Location,
            'distance': (None, int, float),
            'duration': timedelta,
            'path': (None, (Coordinates, ))
        }

    def _serialize(self, depth):
        data = {}
        self._serial_add(data, 'distance')
        data['duration'] = int(self.duration.total_seconds())
        data['origin'] = self.origin.serialize(depth, True)
        data['destination'] = self.destination.serialize(depth, True)
        if self.path is not None:
            data['path'] = [p.serialize() for p in self.path]
        return data

    def _unserialize(self, data):
        types = (Location, Stop, POI, Address, Coordinates)
        self._serial_get(data, 'distance')
        self.duration = timedelta(seconds=data['duration'])
        self.origin = self._unserialize_typed(data['origin'], types)
        self.destination = self._unserialize_typed(data['destination'], types)
        if 'path' in data:
            self.path = [Coordinates.unserialize(p) for p in data['path']]

    def __eq__(self, other):
        assert isinstance(other, Way)
        return (self.origin == other.origin and
                self.destination == other.destination)
