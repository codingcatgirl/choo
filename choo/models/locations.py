#!/usr/bin/env python3
from .base import Serializable, Searchable, Collectable
from . import fields


class Coordinates(Serializable):
    lat = fields.Field(float, none=False)
    lon = fields.Field(float, none=False)

    def __init__(self, lat=None, lon=None):
        super().__init__()
        self.lat = lat
        self.lon = lon

    def _serialize_instance(self):
        return [self.lat, self.lon]

    def _unserialize(self, data):
        self.lat, self.lon = data

    def __eq__(self, other):
        return isinstance(other, Coordinates) and other.lat == self.lat and other.lon == self.lon

    def __repr__(self):
        return 'Coordinates(%.6f, %.6f)' % (self.lat, self.lon)


class AbstractLocation(Collectable):
    coords = fields.Model(Coordinates)

    def __init__(self, coords=None):
        super().__init__()
        self.coords = coords

    def __repr__(self):
        return 'AbstractLocation(%s)' % (repr(self.coords) if self.coords else '')

    def _near(self, other):
        return self.coords is not None and other.coords is not None and abs(self.coords.lat - other.coords.lat) < 0.02 and abs(self.coords.lon - other.coords.lon) < 0.02

    def _toofar(self, other):
        return (self.coords is not None and other.coords is not None) and (abs(self.coords.lat - other.coords.lat) > 0.04 or abs(self.coords.lon - other.coords.lon) > 0.04)

    def __eq__(self, other):
        return self.coords == other.coords

    _update_default = ('coords', )


class Platform(AbstractLocation):
    stop = fields.Model('Stop', none=False)
    name = fields.Field(str)
    full_name = fields.Field(str)

    def __init__(self, stop=None, name=None, full_name=None):
        super().__init__()
        self.stop = stop
        self.name = name
        self.full_name = full_name

    _update_default = ('name', 'full_name')

    def _update(self, other, better):
        self.stop.update(other.stop)

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
    name = fields.Field(str, none=False)
    near_stops = fields.Model('Stop.Results')

    def __init__(self, country=None, city=None, name=None):
        super().__init__()
        self.country = country
        self.city = city
        self.name = name
        self.near_stops = None

    _update_default = ('country', )

    @property
    def full_name(self):
        if self.city is None:
            return self.name
        else:
            return '%s, %s' % (self.city, self.name)

    def _update(self, other, better):
        if better or (self.city is None and other.city is not None):
            if other.city is not None:
                self.city = other.city
            self.name = other.name

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

        if self.city is None:
            if other.city is None:
                return near or self.name.replace(',', '').replace('  ', ' ') == other.name.replace(',', '').replace('  ', ' ')

            else:
                if not self.name.endswith(other.name):
                    return False

                if self.name.startswith(other.city):
                    return True

                return near
        else:
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
    train_station_name = fields.Field(str)

    def __init__(self, country=None, city=None, name=None):
        super().__init__()
        Location.__init__(self, country, city, name)
        self.rides = None
        self.lines = None
        self.train_station_name = None

    def _update(self, other, better):
        if ('uic' not in self._ids and 'uic' in self._ids) or self.train_station_name is None:
            self.train_station_name = other.train_station_name

    @property
    def full_name(self):
        if self.train_station_name is not None:
            return self.train_station_name
        elif self.city is None:
            return self.name
        else:
            return '%s, %s' % (self.city, self.name)

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

            if self._near(other) and (self.train_station_name.endswith(other.train_station_name) or other.train_station_name.endswith(self.train_station_name)):
                return True

        return self._location_eq(other)


class POI(Location):
    def __init__(self, country=None, city=None, name=None):
        super().__init__()
        Location.__init__(self, country, city, name)

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

    def __init__(self, country=None, city=None, name=None):
        super().__init__()
        Location.__init__(self, country, city, name)
        self.street = None
        self.number = None

    _update_default = ('street', 'number')

    def __eq__(self, other):
        if not isinstance(other, POI):
            return False

        byid = self._equal_by_id(other)
        if byid is not None:
            return byid

        return self._location_eq(other)
