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

    def _serialize(self):
        return [self.lat, self.lon]

    def _unserialize(self, data):
        self.lat, self.lon = data

    def __eq__(self, other):
        assert isinstance(other, Coordinates)
        return other.lat == self.lat and other.lon == self.lon

    def __repr__(self):
        return 'Coordinates(%.6f, %.6f)' % (self.lat, self.lon)


class AbstractLocation(ModelBase):
    def __init__(self, coords=None):
        super().__init__()
        self.coords = coords

    @classmethod
    def _validate(cls):
        return {
            'coords': (None, Coordinates),
        }

    def __repr__(self):
        return 'AbstractLocation(%s)' % (repr(self.coords) if self.coords else '')


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

    def __repr__(self):
        return 'Platform(%s, %s, %s)' % (repr(self.stop), repr(self.name), repr(self.full_name))


class Location(AbstractLocation):
    def __init__(self, country=None, city=None, name=None):
        super().__init__()
        self.country = country
        self.city = city
        self.name = name
        self.near_stops = []

    @classmethod
    def _validate(cls):
        return {
            'country': (None, str),
            'city': (None, str),
            'name': str,
            'near_stops': None
        }

    @property
    def full_name(self):
        if self.city is None:
            return self.name
        else:
            return '%s, %s' % (self.city, self.name)

    def _validate_custom(self, name, value):
        if name == 'near_stops':
            for v in value:
                if not isinstance(v, Location):
                    return False
            return True

    def _serialize_custom(self, name):
        if name == 'near_stops':
            return 'near_stops', [s.serialize() for s in self.near_stops]

    def _unserialize_custom(self, name, data):
        if name == 'near_stops':
            self.near_stops = [Stop.unserialize(s) for s in data]

    def __repr__(self):
        return '%s(%s, %s, %s)' % (self.__class__.__name__, repr(self.country), repr(self.city), repr(self.name))


class Stop(Location):
    def __init__(self, country=None, city=None, name=None):
        super().__init__()
        Location.__init__(self, country, city, name)
        self.rides = []
        self.lines = []
        self.train_station_name = None

    @classmethod
    def _validate(cls):
        return {
            'rides': None,
            'lines': None,
            'train_station_name': (None, str)
        }

    def _validate_custom(self, name, value):
        from .ride import RideSegment
        from .line import Line
        if name == 'rides':
            for v in value:
                if not isinstance(v, RideSegment):
                    return False
            return True
        elif name == 'lines':
            for v in value:
                if not isinstance(v, Line):
                    return False
            return True

    @property
    def full_name(self):
        if self.train_station_name is not None:
            return self.train_station_name
        elif self.city is None:
            return self.name
        else:
            return '%s, %s' % (self.city, self.name)

    def _serialize_custom(self, name):
        if name == 'rides':
            return 'rides', [ride.serialize() for ride in self.rides]
        elif name == 'lines':
            return 'lines', [line.serialize() for line in self.lines]

    def _unserialize_custom(self, name, data):
        from .ride import RideSegment
        from .line import Line
        if name == 'rides':
            self.rides = [RideSegment.unserialize(r) for r in data]
        elif name == 'lines':
            self.lines = [Line.unserialize(line) for line in data]

    def __repr__(self):
        return '<Stop %s>' % repr(self.full_name)

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
    def __init__(self, country=None, city=None, name=None):
        super().__init__()
        Location.__init__(self, country, city, name)


class Address(Location):
    def __init__(self, country=None, city=None, name=None):
        super().__init__()
        Location.__init__(self, country, city, name)
        self.street = None
        self.number = None

    @classmethod
    def _validate(cls):
        return {
            'street': (None, str),
            'number': (None, str),
        }
