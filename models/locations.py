#!/usr/bin/env python3
from .base import ModelBase, Serializable


class Coordinates(Serializable):
    def __init__(self, lat=None, lon=None):
        self.lat = lat
        self.lon = lon

    @classmethod
    def _validate(cls):
        return {
            'lat': float,
            'lon': float
        }

    def _serialize(self, depth):
        return [self.lat, self.lon]

    def _unserialize(self, data):
        self.lat, self.lon = data

    def __eq__(self, other):
        assert isinstance(other, Coordinates)
        return other.lat == self.lat and other.lon == self.lon

    def __repr__(self):
        return '<Coordinates %.6f %.6f>' % (self.lat, self.lon)


class AbstractLocation(ModelBase):
    def __init__(self, coords=None):
        super().__init__()
        self.coords = coords

    @classmethod
    def _validate(cls):
        return {
            'coords': (None, Coordinates),
        }

    def _serialize(self, depth):
        data = {}
        if self.coords:
            data['coords'] = self.coords.serialize()
        return data

    def _unserialize(self, data):
        if 'coords' in data:
            self.coords = Coordinates.unserialize(data['coords'])


class Platform(AbstractLocation):
    def __init__(self, stop=None, name=None, full_name=None):
        super().__init__()
        self.stop = stop
        self.name = name
        self.full_name = full_name

    @classmethod
    def _validate(cls):
        return {
            'stop': Stop,
            'name': (str, None),
            'full_name': (str, None),
        }

    def _serialize(self, depth):
        data = {}
        data['stop'] = self.stop.serialize()
        if self.name is not None:
            data['name'] = self.name
        if self.full_name is not None:
            data['full_name'] = self.full_name
        return data

    def _unserialize(self, data):
        self.stop = Stop.unserialize(data['stop'])
        if 'name' in data:
            self.name = data['name']
        if 'full_name' in data:
            self.full_name = data['full_name']

    def __repr__(self):
        return '<Platform %s %s>' % (repr(self.stop), repr(self.full_name))


class Location(AbstractLocation):
    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        self.country = country
        self.city = city
        self.name = name
        self.full_name = '%s, %s' % (city, name) if city is not None else name
        self.near_stops = []

    @classmethod
    def _validate(cls):
        return {
            'country': (None, str),
            'city': (None, str),
            'name': str,
            'near_stops': ((Location, ), )
        }

    def _serialize(self, depth):
        data = {}
        self._serial_add(data, 'country')
        self._serial_add(data, 'city')
        data['name'] = self.name
        if self.near_stops:
            data['near_stops'] = [s.serialize() for s in self.near_stops]
        return data

    def _unserialize(self, data):
        self._serial_get(data, 'country')
        self._serial_get(data, 'city')
        self._serial_get(data, 'name')
        if 'coords' in data:
            self.coords = Coordinates.unserialize(data['coords'])
        if 'near_stops' in data:
            self.near_stops = [Stop.unserialize(s) for s in data['near_stops']]


class Stop(Location):
    _serialize_depth = 5

    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)
        self.rides = []
        self.lines = []

    @classmethod
    def _validate(cls):
        from .ride import RideSegment
        from .line import Line
        return {
            'rides': (None, (RideSegment, )),
            'lines': (None, (Line, ))
        }

    def _serialize(self, depth):
        data = {}
        if depth:
            if self.rides is not None:
                data['rides'] = [ride.serialize(depth) for ride in self.rides]
            if self.lines is not None:
                data['lines'] = [line.serialize(depth) for line in self.lines]
        return data

    def _unserialize(self, data):
        from .ride import RideSegment
        from .line import Line
        self._serial_get(data, 'country')
        self._serial_get(data, 'city')
        self._serial_get(data, 'name')
        if 'rides' in data:
            self.rides = [RideSegment.unserialize(r) for r in data['rides']]
        if 'lines' in data:
            self.lines = [Line.unserialize(line) for line in data['lines']]

    def __repr__(self):
        return '<%s %s, %s>' % ('Stop', self.city, self.name)

    def __eq__(self, other):
        assert isinstance(other, Stop)
        for k, id_ in self._ids.items():
            if id_ is not None and other._ids.get(k) == id_:
                return True
        if self.coords is not None and self.coords == other.coords:
            return True
        return (self.name is not None and self.name == other.name and
                self.city == other.city and self.country == other.country)


class POI(Location):
    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)


class Address(Location):
    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)
