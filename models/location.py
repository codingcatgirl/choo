#!/usr/bin/env python3
from .base import ModelBase, Serializable
from datetime import timedelta


class Coordinates(Serializable):
    _validate = {
        'lat': float,
        'lon': float
    }

    def __init__(self, lat=None, lon=None):
        self.lat = lat
        self.lon = lon

    def _serialize(self, depth):
        return [self.lat, self.lon]

    def _unserialize(self, data):
        self.lat, self.lon = data


class Location(ModelBase):
    _validate = {
        'country': (None, str),
        'city': (None, str),
        'name': str,
        'coords': (None, Coordinates)
    }

    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        self.country = country
        self.city = city
        self.name = name
        self.coords = coords

    def _serialize(self, depth):
        data = {}
        self._serial_add(data, 'country')
        self._serial_add(data, 'city')
        data['name'] = self.name
        if self.coords:
            data['coords'] = self.coords.serialize()
        return data

    def _unserialize(self, data):
        self._serial_get(data, 'country')
        self._serial_get(data, 'city')
        self._serial_get(data, 'name')
        if 'coords' in data:
            self.coords = Coordinates.unserialize(data['coords'])


class POI(Location):
    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)


class Address(Location):
    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)


class Way(ModelBase):
    _validate = {
        'origin': Location,
        'destination': Location,
        'distance': (int, float),
        'duration': timedelta,
        'path': (None, (Coordinates, ))
    }

    def __init__(self, origin=None, destination=None, distance=None):
        super().__init__()
        self.origin = origin
        self.destination = destination
        self.distance = None
        self.duration = None
        self.path = None
        # todo: self.stairs = None

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
        from .main import Stop
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
