#!/usr/bin/env python3
from .base import Serializable, TripPart
from .locations import AbstractLocation, Coordinates
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
            'path': None,
        }

    def _validate_custom(self, name, value):
        if name == 'path':
            if value is None:
                return True
            for v in value:
                if not isinstance(v, Coordinates):
                    return False
            return True

    def _serialize_custom(self, name):
        if name == 'path':
            return 'path', [p.serialize() for p in self.path]

    def _unserialize_custom(self, name, data):
        if name == 'path':
            self.path = [Coordinates.unserialize(p) for p in data]

    def __eq__(self, other):
        assert isinstance(other, Way)
        return (self.origin == other.origin and
                self.destination == other.destination)

    def __repr__(self):
        distance = ''
        if self.distance:
            distance = ' %dm' % self.distance
        return '<Way %s %dmin%s %s %s>' % (str(self.waytype), self.duration.total_seconds() / 60, distance, repr(self.origin), repr(self.destination))


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

    def _serialize(self):
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
