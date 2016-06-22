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


class IDs(Serializable):
    def __init__(self, initialdata={}):
        self.data = {name: (value if isinstance(value, (set, list)) else set((value, )))
                     for name, value in initialdata.items()}

    def __getitem__(self, name):
        return next(iter(self.data[name]))

    def __setitem__(self, name):
        raise TypeError('Use IDs.add()')

    def __delitem__(self, name):
        del self.data[name]

    def __contains__(self, name):
        return name in self.data

    def clear(self):
        self.data = {}

    def copy(self):
        return self.__class__(self.data)

    def keys(self):
        return self.data.keys()

    def add(self, name, value):
        self.data.setdefault(name, set()).add(value)

    def remove(self, name, value):
        self.data[name].remove(value)

    def discard(self, name, value):
        self.data.get(name, set()).discard(value)

    def get(self, name, default=None):
        return self[name] if name in self.data else default

    def __len__(self):
        return sum((len(values) for values in self.data.values()), 0)

    def getall(self, name):
        return frozenset(self.data.get(name, set()))

    def items(self):
        for name, values in self.data.items():
            for value in values:
                yield name, value

    def values(self):
        return (value for name, value in self.items())

    def update(self, other):
        for name, value in other.items():
            self.data.setdefault(name, set()).update(value if isinstance(value, set) else set(value))

    def serialize(self):
        return {name: (tuple(values) if len(values)-1 else next(iter(values)))
                for name, values in self.data.items() if values}

    @classmethod
    def unserialize(self, data):
        return self.__class__(data)


class FrozenIDs(IDs):
    def add(self, name, value):
        raise TypeError('FrozenIDs can not be altered')

    def __delitem__(self, name):
        raise TypeError('FrozenIDs can not be altered')

    def remove(self, name, value):
        raise TypeError('FrozenIDs can not be altered')

    def clear(self, name, value):
        raise TypeError('FrozenIDs can not be altered')

    def discard(self, name, value):
        raise TypeError('FrozenIDs can not be altered')

    def update(self, other):
        raise TypeError('FrozenIDs can not be altered')


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


class LiveTime(Serializable, namedtuple('LiveTime', ('time', 'delay'))):
    def __new__(self, time, delay=None):
        if not isinstance(time, datetime):
            raise TypeError('time has to be datetime, not %s' % repr(time))

        if not isinstance(delay, timedelta):
            raise TypeError('delay has to be timedelta or None, not %s' % repr(delay))

        return super().__new__(time, delay)

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
