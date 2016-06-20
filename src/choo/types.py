from abc import ABC, abstractmethod
from collections import namedtuple
from datetime import datetime, timedelta
from enum import Enum
from math import asin, cos, radians, sin, sqrt


class Serializable(ABC):
    @abstractmethod
    def serialize(self):
        pass

    @classmethod
    @abstractmethod
    def unserialize(cls, data):
        pass


class Coordinates(Serializable, namedtuple('Coordinates', ('lat', 'lon'))):
    def distance_to(self, other):
        if not isinstance(other, Coordinates):
            raise TypeError('distance_to expected Coordinates object, not %s' % repr(other))

        lon1, lat1, lon2, lat2 = map(radians, [self.lon, self.lat, other.lon, other.lat])
        return 12742000 * asin(sqrt(sin((lat2-lat1)/2)**2+cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2))

    def serialize(self):
        return (self.lat, self.lon)

    @classmethod
    def unserialize(cls, data):
        return cls(*data)

    def __reversed__(self):
        return tuple(self)[::-1]

    def _near(self, other):
        return (abs(self.lat - other.lat) < 0.02 and
                abs(self.lon - other.lon) < 0.02)

    def _not_too_far(self, other):
        return (abs(self.lat - other.lat) < 0.04 or
                abs(self.lon - other.lon) < 0.04)


class LiveTime:
    def __init__(self, time=None, delay=None, expected_time=None, **kwargs):
        if expected_time is not None:
            if time is None:
                time = expected_time - delay
            elif delay is None:
                delay = expected_time - time
            elif expected_time - time != delay:
                raise ValueError

        super().__init__(time=time, delay=delay, **kwargs)

    def __repr__(self):
        return '<LiveTime %s>' % (str(self))

    def __str__(self):
        out = self.time.strftime('%Y-%m-%d %H:%M')
        if self.delay is not None:
            out += ' %+d' % (self.delay.total_seconds() / 60)
        return out

    @property
    def is_live(self):
        return self.delay is not None

    @property
    def expected_time(self):
        if self.delay is not None:
            return self.time + self.delay
        else:
            return self.time

    def __add__(self, other):
        assert isinstance(other, timedelta)
        return LiveTime(self.time + other, self.delay)

    def __sub__(self, other):
        assert isinstance(other, timedelta)
        return LiveTime(self.time - other, self.delay)

    def __eq__(self, other):
        if isinstance(other, datetime):
            return self.expected_time == other
        elif isinstance(other, LiveTime):
            return self.time == other.time
        return False

    def __lt__(self, other):
        assert isinstance(other, LiveTime) or isinstance(other, datetime)
        if isinstance(other, datetime):
            return self.expected_time < other
        else:
            return self.expected_time < other.expected_time

    def __gt__(self, other):
        assert isinstance(other, LiveTime) or isinstance(other, datetime)
        if isinstance(other, datetime):
            return self.expected_time < other
        else:
            return self.expected_time < other.expected_time


class IFOPT(Serializable):
    @classmethod
    def parse(cls, string):
        if string is None:
            return None

        try:
            return cls(*string.split(':'))
        except TypeError:
            # Wrong number of arguments
            return None

    def __str__(self):
        return ':'.join(self)

    def serialize(self):
        return str(self)

    @classmethod
    def unserialize(cls, data):
        return cls.parse(data)


class StopIFOPT(IFOPT, namedtuple('StopIFOPT', ('country', 'area', 'stop'))):
    pass


class StopAreaIFOPT(IFOPT, namedtuple('StopAreaIFOPT', ('country', 'area', 'stop', 'level'))):
    def get_stop_ifopt(self):
        return StopIFOPT(*self[:3])


class PlatformIFOPT(IFOPT, namedtuple('PlatformIFOPT', ('country', 'area', 'stop', 'level', 'quay'))):
    def get_area_ifopt(self):
        return StopAreaIFOPT(*self[:4])

    def get_stop_ifopt(self):
        return StopIFOPT(*self[:3])


class SerializableEnumMixin:
    def serialize(self):
        return self.name

    @classmethod
    def unserialize(cls, data):
        result = getattr(cls, data)
        if not isinstance(result, cls):
            raise AttributeError
        return result

Serializable.register(SerializableEnumMixin)


class HierarchicEnumMixin(SerializableEnumMixin):
    def __contains__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError('can only match %s instances' % self.__class__.__name__)
        return self.value in other.value

    def __iter__(self):
        return (e for e in self.__class__ if self.value in e.value)

    def contained_in(self):
        return (e for e in self.__class__ if e.value in self.value)


class WayType(HierarchicEnumMixin, Enum):
    any = '_'

    walk = '_walk_'
    bike = '_bike_'
    car = '_car_'
    taxi = '_taxi_'

    def __repr__(self):
        return 'WayType.' + self.name


class WayEvent(HierarchicEnumMixin, Enum):
    any = '_'
    up = '_up_'
    down = '_down_'

    stairs = '_stairs_'
    stairs_up = '_stairs_up_'
    stairs_down = '_stairs_down_'
    elevator = '_elevator_'
    elevator_up = '_elevator_up_'
    elevator_down = '_elevator_down_'
    escalator = '_escalator_'
    escalator_up = '_escalator_up_'
    escalator_down = '_escalator_down_'

    def __repr__(self):
        return 'WayEvent.' + self.name


class WalkSpeed(SerializableEnumMixin, Enum):
    normal = 'normal'
    fast = 'fast'
    slow = 'slow'

    def __repr__(self):
        return 'WalkSpeed.' + self.name


class LineType(HierarchicEnumMixin, Enum):
    any = '_'

    train = '_train_'
    train_local = '_train_local_'
    train_longdistance = '_train_longdistance_'
    train_longdistance_normal = '_train_longdistance_normal_'
    train_longdistance_highspeed = '_train_longdistance_highspeed_'
    urban = '_urban_'
    metro = '_metro_'
    tram = '_tram_'
    bus = '_bus_'
    bus_regional = '_bus_regional_'
    bus_city = '_bus_city_'
    bus_express = '_bus_express_'
    bus_longdistance = '_bus_longdistance_'
    suspended = '_suspended_'
    ship = '_ship_'
    dialable = '_dialable_'
    other = '_other_'

    def __repr__(self):
        return 'LineType.' + self.name


class POIType(SerializableEnumMixin, Enum):
    unknown = 'unknown'
    bicycle_hire = 'bicycle_hire'
    education = 'education'
    graveyard = 'graveyard'
    mall = 'mall'
    parking = 'parking'
    place_of_worship = 'place_of_worship'
    public_building = 'public_building'
    sight = 'sight'
    sport = 'sport'
    swimming = 'swimming'
    venue = 'venue'


class PlatformType(SerializableEnumMixin, Enum):
    unknown = 'unknown'
    street = 'street'
    platform = 'platform'


class LineTypes:
    def __init__(self, *linetypes):
        self._linetypes = set()
        for linetype in linetypes:
            if not isinstance(linetype, LineType):
                raise TypeError('expected LineType instance, got %s' % repr(linetype))
            self._linetypes |= set(linetype) | set(linetype.contained_in())

    def exclude(self, *linetypes):
        expanded = self._linetypes
        for linetype in linetypes:
            if not isinstance(linetype, LineType):
                raise TypeError('expected LineType instance, got %s' % repr(linetype))
            expanded -= set(linetype)

        r = LineTypes()
        r._linetypes = expanded
        return r

    def include(self, *linetypes):
        expanded = self._linetypes
        for linetype in linetypes:
            if not isinstance(linetype, LineType):
                raise TypeError('expected LineType instance, got %s' % repr(linetype))
            expanded |= set(linetype) | set(linetype.contained_in())

        r = LineTypes()
        r._linetypes = expanded
        return r

    def __iter__(self):
        complete = set(lt for lt in self._linetypes if set(lt).issubset(self._linetypes))
        return (lt for lt in complete if not ((set(lt.contained_in())-set(lt)) & complete))

    def __contains__(self, linetype):
        if not isinstance(linetype, linetype):
            raise TypeError('can only match LineType instances')
        return linetype in self._linetypes

    def __repr__(self):
        return 'LineTypes(%s)' % ', '.join(str(lt) for lt in self)

LineTypes.any = LineTypes(LineType.any)
LineTypes.none = LineTypes()
