#!/usr/bin/env python3
from .base import ModelBase, Serializable, TripPart
from .locations import Coordinates, AbstractLocation, Location, Platform, Stop, POI, Address
from datetime import timedelta


class Way(TripPart):
    def __init__(self, waytype=None, origin=None, destination=None, distance=None):
        super().__init__()
        self.waytype = WayType('walk') if waytype is None else waytype
        self.origin = origin
        self.destination = destination
        self.distance = None
        self.duration = None
        self.path = None

    @classmethod
    def _validate(cls):
        return {
            'waytype': WayType,
            'origin': AbstractLocation,
            'destination': AbstractLocation,
            'distance': (None, int, float),
            'duration': timedelta,
            'path': (None, (Coordinates, ))
        }

    def _serialize(self, depth):
        data = {}
        self._serial_add(data, 'distance')
        data['waytype'] = self.waytype.serialize()
        data['duration'] = int(self.duration.total_seconds())
        data['origin'] = self.origin.serialize(depth, True)
        data['destination'] = self.destination.serialize(depth, True)
        if self.path is not None:
            data['path'] = [p.serialize() for p in self.path]
        return data

    def _unserialize(self, data):
        types = (AbstractLocation, Location, Stop, Platform, POI, Address)
        self._serial_get(data, 'distance')
        self.duration = timedelta(seconds=data['duration'])
        self.waytype = WayType.unserialize(data.get('waytype', 'walk'))
        self.origin = self._unserialize_typed(data['origin'], types)
        self.destination = self._unserialize_typed(data['destination'], types)
        if 'path' in data:
            self.path = [Coordinates.unserialize(p) for p in data['path']]

    def __eq__(self, other):
        assert isinstance(other, Way)
        return (self.origin == other.origin and
                self.destination == other.destination)


class WayType(Serializable):
    _known = ('walk', 'bike', 'car', 'taxi')
    _created = {}

    def __new__(cls, value=''):
        if isinstance(value, cls):
            return value
        elif value not in cls._known:
            raise AttributeError('invalid waytype: %s' % repr(value))
        if value in cls._created:
            return cls._created[value]
        else:
            self = super().__new__(cls)
            self._value = value
            cls._created[value] = self
            return self

    def _serialize(self, depth):
        return self._value

    @classmethod
    def unserialize(cls, data):
        return cls(data)

    def __repr__(self):
        return 'WayType(%s)' % repr(self._value)

    def __str__(self):
        return self._value

    def __equals__(self, other):
        return other._value == self._value
