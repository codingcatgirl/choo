#!/usr/bin/env python3
from .base import Serializable, Searchable, Collectable
from . import fields


class Coordinates(Serializable):
    lat = fields.Field(float, none=False)
    lon = fields.Field(float, none=False)

    def __init__(self, lat=None, lon=None, **kwargs):
        super().__init__(lat=lat, lon=lon, **kwargs)

    def _serialize_instance(self):
        return [self.lat, self.lon]

    @classmethod
    def unserialize(cls, data):
        return cls(*data)

    def __eq__(self, other):
        return isinstance(other, Coordinates) and other.lat == self.lat and other.lon == self.lon

    def __repr__(self):
        return 'Coordinates(%.6f, %.6f)' % (self.lat, self.lon)


class AbstractLocation(Collectable):
    coords = fields.Model(Coordinates)

    def __init__(self, **kwargs):
        # magic, do not remove
        super().__init__(**kwargs)

    def __repr__(self):
        return 'AbstractLocation(%s)' % (repr(self.coords) if self.coords else '')

    def _near(self, other):
        return (self.coords is not None and other.coords is not None and
                abs(self.coords.lat - other.coords.lat) < 0.02 and
                abs(self.coords.lon - other.coords.lon) < 0.02)

    def _toofar(self, other):
        return ((self.coords is not None and other.coords is not None) and
                (abs(self.coords.lat - other.coords.lat) > 0.04 or
                 abs(self.coords.lon - other.coords.lon) > 0.04))

    def __eq__(self, other):
        return self.coords == other.coords


class Platform(AbstractLocation):
    stop = fields.Model('Stop', none=False)
    ifopt = fields.Field(tuple)
    name = fields.Field(str)
    full_name = fields.Field(str)

    def __init__(self, stop=None, name=None, full_name=None, **kwargs):
        super().__init__(stop=stop, name=name, full_name=full_name, **kwargs)

    def __repr__(self):
        return 'Platform(%s, %s, %s)' % (repr(self.stop), repr(self.name), repr(self.full_name))

    def __eq__(self, other):
        if not isinstance(other, Platform):
            return False

        if self.stop != other.stop:
            return False

        byid = self._equal_by_id(other)
        if byid is not None:
            return byid

        if self.name is not None and self.name == other.name:
            return True

        if self.full_name is not None and self.full_name == other.full_name:
            return True

        if self.coords is not None and self.coords == other.coords:
            return True

        return False


class Location(AbstractLocation):
    country = fields.Field(str)
    city = fields.Field(str)
    name = fields.Field(str)
    near_stops = fields.Model('Stop.Results')

    def __init__(self, country=None, city=None, name=None, **kwargs):
        super().__init__(country=country, city=city, name=name, **kwargs)

    def __repr__(self):
        return '%s(%s, %s, %s)' % (self.__class__.__name__, repr(self.country), repr(self.city), repr(self.name))

    def __eq__(self, other):
        if not isinstance(other, Location):
            return False

        byid = self._equal_by_id(other)
        if byid is not None:
            return byid

        return self._location_eq(other)

    def _location_eq(self, other):
        if self.coords == other.coords and self.coords is not None:
            return True

        if self.country is not None and other.country is not None and self.country != other.country:
            return False

        near = self._near(other)

        if self.city is not None:
            if other.city is None:
                if not other.name.endswith(self.name):
                    return False

                if other.name.startswith(self.city):
                    return True

                return near
            else:
                if self.name != other.name:
                    return False

                return near or self.city == other.city

        if other.city is None:
            return (near or
                    self.name.replace(',', '').replace('  ', ' ') == other.name.replace(',', '').replace('  ', ' '))
        else:
            if not self.name.endswith(other.name):
                return False

            if self.name.startswith(other.city):
                return True

            return near

    class Request(Searchable.Request):
        name = fields.Field(str)
        city = fields.Field(str)

        def __init__(self):
            super().__init__()
            self.name = None
            self.city = None


class Stop(Location):
    rides = fields.Model('Ride.Results')
    lines = fields.Model('Line.Results')
    full_name = fields.Field(str)
    ifopt = fields.Any()
    train_station_name = fields.Field(str)

    def __init__(self, country=None, city=None, name=None, **kwargs):
        super().__init__(country=country, city=city, name=name, **kwargs)

    def __repr__(self):
        return '<Stop %s>' % repr(self.full_name)

    def __eq__(self, other):
        if not isinstance(other, Stop):
            return False

        byid = self._equal_by_id(other)
        if byid is not None:
            return byid

        if self.country is not None and other.country is not None and self.country != other.country:
            return False

        if self.train_station_name is not None and other.train_station_name is not None:
            if self.train_station_name.replace('-', ' ') == other.train_station_name.replace('-', ' '):
                return True

            if self._near(other) and (self.train_station_name.endswith(other.train_station_name) or
                                      other.train_station_name.endswith(self.train_station_name)):
                return True

        return self._location_eq(other)


class POI(Location):
    def __init__(self, country=None, city=None, name=None, **kwargs):
        super().__init__(country=country, city=city, name=name, **kwargs)

    @property
    def full_name(self):
        if self.city is None:
            return self.name
        else:
            return '%s, %s' % (self.city, self.name)

    def __eq__(self, other):
        if not isinstance(other, POI):
            return False

        byid = self._equal_by_id(other)
        if byid is not None:
            return byid

        return self._location_eq(other)


class Address(Location):
    street = fields.Field(str)
    number = fields.Field(str)

    def __init__(self, country=None, city=None, name=None, **kwargs):
        super().__init__(country=country, city=city, name=name, **kwargs)

    @property
    def full_name(self):
        if self.city is None:
            return self.name
        else:
            return '%s, %s' % (self.city, self.name)

    def __eq__(self, other):
        if not isinstance(other, POI):
            return False

        byid = self._equal_by_id(other)
        if byid is not None:
            return byid

        return self._location_eq(other)
