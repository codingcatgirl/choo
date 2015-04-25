#!/usr/bin/env python3
from .base import ModelBase

class Location(ModelBase):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        self.country = country
        self.city = city
        self.name = name
        self.coords = coords

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'country')
        self._serial_get(data, 'city')
        self._serial_get(data, 'name')
        self._serial_get(data, 'coords')

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, 'country', ids,)
        self._serial_add(data, 'city', ids)
        self._serial_add(data, 'name', ids)
        self._serial_add(data, 'coords', ids)
        return data


class Stop(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)
        self.rides = []
        self.lines = []

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'rides')
        self._serial_get(data, 'lines')
        self.rides = [ModelBase.unserialize(ride) for ride in self.rides]
        self.lines = [ModelBase.unserialize(line) for line in self.lines]

    def __repr__(self):
        return '<%s %s, %s>' % ('Stop', self.city, self.name)

    def __eq__(self, other):
        if not isinstance(other, Stop):
            return None
        for k, id_ in self._ids.items():
            if id_ is not None and other._ids.get(k) == id_:
                return True
        if self.coords is not None and self.coords == other.coords:
            return True
        return self.name is not None and self.name == other.name and self.city == other.city and self.country == other.country

    def _serialize(self, ids):
        data = {}
        if self.rides:
            rides = [ride.serialize(ids) for ride in self.rides]
            if rides.count({}) == len(rides):
                rides = []
            self._serial_add(data, 'rides', ids, val=rides)

        if self.lines:
            lines = [line.serialize(ids) for line in self.lines]
            if lines.count({}) == len(lines):
                lines = []
            self._serial_add(data, 'lines', ids, val=lines)
        return data


class POI(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)

    def _serialize(self, ids):
        return {}


class Address(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)

    def _serialize(self, ids):
        return {}
