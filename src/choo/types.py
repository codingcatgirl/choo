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
    """
    A Mapping of ids by id namespace (e.g. 'vrr' for the id namespace of the VRR network)
    Multiple ids per namespace are possible.
    IDs instances can be combined like sets.

    How to initializ:
    >>> ids = IDs((('one_id', '1a'), ('multiple_ids', 2), ('multiple_ids', 3)))
    >>> ids = IDs({'one_id': '1a', 'multiple_ids': (2, 3)})

    How to retrieve data:
    >>> ids['multiple_ids']  # returns 2 or 3
    >>> ids.getall('multiple_ids')  # returns set((2, 3))
    >>> ids['other_namespace']  # KeyError
    >>> ids.get('other_namespace', None)  # returns None
    >>> tuples(ids.items())  # (('one_id', '1a'), ('multiple_ids', 2), ('multiple_ids', 3))

    How to add data:
    >>> ids['multiple_ids'] = 4  # TypeError
    >>> ids.add('multiple_ids', 4)  # this works
    >>> ids.update({'multiple_ids': 4})  # this works
    >>> ids.update((('multiple_ids', 4)))  # this also works
    >>> ids.update({'multiple_ids': set((4, 5))})  # this works, too
    >>> ids |= {'multiple_ids': 4} # even this works
    >>> ids |= IDs({'multiple_ids': 4}) # and this

    How to remove data:
    >>> del ids['multiple_ids']  # deletes all ids from this namespace
    >>> ids.remove('multiple_ids', 3)  # this works
    >>> ids.remove('multiple_ids', 7)  # KeyError
    >>> ids.discard('multiple_ids', 7)  # does nothing
    >>> ids.clear()  # clear completely

    How to compare:
    >>> len(ids)  # how many ids in total
    >>> ids & IDs({'multiple_ids': 3})  # returns IDs({'multiple_ids': 3})
    >>> ids & IDs({'multiple_ids': 9})  # returns IDs({})
    >>> if ids & IDs({'multiple_ids': 9}):
    ...     pass  # this gets executed if there are common ids
    """
    def __init__(self, initialdata={}):
        """
        Initialize the IDs object.
        Works exactly like initializing a dict – initialdata can be dict or a iterable of 2-tuples.

        There are two ways to give multiple ids:
        >>> ids = IDs((('one_id', '1a'), ('multiple_ids', 2), ('multiple_ids', 3)))
        >>> ids = IDs({'one_id': '1a', 'multiple_ids': (2, 3)})

        """
        items = initialdata.items() if isinstance(initialdata, (dict, IDs)) else initialdata
        self.data = {name: (value if isinstance(value, (set, list, tuple)) else set((value, )))
                     for name, value in items}

    def __getitem__(self, name):
        """
        Get any ID from this namespace or raise KeyError
        """
        return next(iter(self.data[name]))

    def __setitem__(self, name):
        """
        Not supported, use .add()
        """
        raise TypeError('Use IDs.add()')

    def __delitem__(self, name):
        """
        Delete all IDs from this namespace
        """
        del self.data[name]

    def __contains__(self, name):
        """
        Check if any ids from this namespace are contained
        """
        return name in self.data

    def __iter__(self):
        """
        Iterate over namespaces
        """
        return iter(self.data)

    def clear(self):
        """
        Clear data
        """
        self.data = {}

    def copy(self):
        """
        Return a copy
        """
        return self.__class__(self.data)

    def keys(self):
        """
        Get namespaces
        """
        return self.data.keys()

    def add(self, name, value):
        """
        Add id to namespace
        """
        self.data.setdefault(name, set()).add(value)

    def remove(self, name, value):
        """
        Remove id from namespace.
        Raises KeyError if the namespace did no exist and ValueError if the id did not exist.
        """
        self.data[name].remove(value)
        if not self.data[name]:
            del self.data[name]

    def discard(self, name, value):
        """
        Remove id from namespace if it existed.
        """
        if name not in self.data:
            return

        self.data[name].discard(value)
        if not self.data[name]:
            del self.data[name]

    def get(self, name, default=None):
        """
        Get any id fom this namespace or the default value if there is no id from this namespace.
        """
        return self[name] if name in self.data else default

    def __len__(self):
        """
        Get total count of ids
        """
        return sum((len(values) for values in self.data.values()), 0)

    def getall(self, name):
        """
        Get all ids from this namespace.
        """
        return frozenset(self.data.get(name, set()))

    def items(self):
        """
        Iterate over (namespace, id) tuples.
        """
        for name, values in self.data.items():
            for value in values:
                yield name, value

    def values(self):
        """
        Iterate over all ids.
        """
        return (value for name, value in self.items())

    def update(self, other):
        """
        Update ids using dictionary, iterable or other IDs object.
        """
        for name, value in other.items():
            self.data.setdefault(name, set()).update(value if isinstance(value, (set, list, tuple)) else set(value))

    def serialize(self):
        return {name: (tuple(values) if len(values)-1 else next(iter(values)))
                for name, values in self.data.items() if values}

    def union(self, other):
        """
        Return new IDs object with IDs from this and the other object combined.
        """
        result = self.copy()
        result.update(other)
        return result

    def intersection(self, other):
        """
        Return new IDs object with IDs that are both in this and the other object.
        """
        return self.__class__(set(self.items()) & set(self.__class__(other).items()))

    __and__ = intersection
    __or__ = union
    __ior__ = update

    @classmethod
    def unserialize(self, data):
        return self.__class__(data)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.data)


class FrozenIDs(IDs):
    """
    Like IDs, but can not be altered. Use IDs(frozenids) to get a alterable version.
    """
    def _frozen_error(self, *args, **kwargs):
        raise TypeError('FrozenIDs can not be altered')

    add = _frozen_error
    __delitem__ = _frozen_error
    remove = _frozen_error
    clear = _frozen_error
    discard = _frozen_error
    update = _frozen_error
    __ior__ = _frozen_error


class Coordinates(Serializable, namedtuple('Coordinates', ('lat', 'lon'))):
    """
    Coordinates in WGS84. Has a lat and lon attribute. Implemented as namedtuple.
    """
    def distance_to(self, other):
        """
        Get distance to other Coordinates object in meteres.
        """
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
    """
    Base Class for IFOPT ids. Implemented as namedtuple.
    """

    @classmethod
    def parse(cls, string):
        """
        Parse colon-delimited IFOPT-ID-Notation
        """
        if string is None:
            return None

        try:
            return cls(*string.split(':'))
        except TypeError:
            # Wrong number of arguments
            return None

    def __str__(self):
        """
        Convert to colon-delimited notation.
        """
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
    """
    Mixin for hierarchiv Enums. This enables:
    >>> WayEvent.stairs_up in WayEvent.stairs  # True
    >>> WayEvent.stairs in WayEvent.stairs_up  # False
    >>> WayEvent.stairs in WayEvent.any  # True
    >>> list(WayEvent.stairs)  # [WayEvent.stairs, WayEvent.stairs_up, WayEvent.stairs_down]
    >>> list(WayEvent.stairs_up.contained_in())  # [WayEvent.any, WayEvent.up, WayEvent.stairs, WayEvent.stairs_up]
    """
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
    """
    Selector for LineType objects. LineTypes objects are immutable. All altering methods return a new object.

    How to initialize:
    >>> LineTypes.any  # any line type allowed
    >>> LineTypes.none  # no line type allowed
    >>> LineTypes(LineType.train, LineType.bus)

    How to match:
    >>> LineType.train in LineTypes.any  # True

    How to modify:
    >>> LineTypes.none.include(LineType.train)  # Include all trains
    >>> LineTypes.any.exclude(LineType.train_longdistance_highspeed).  # Exclude LineType.train_longdistance_highspeed
    >>> LineTypes.none.include(LineType.train, Linetype.bus)  # Include all trains and buses

    You can not include a LineType always allows all of its parent types:
    >>> LineType.bus in LineTypes(LineType.bus_regional)  # True
    LineType.bus means “some kind of bus”. You can't allow a regional bus without allowing buses in general.
    This also means that you can not allow a LineType without allowing at least one of its subtypes.

    More examples:
    >>> LineType.any in LineTypes(LineType.bus_regional)  # True
    >>> LineType.train in LineTypes(LineType.bus_regional)  # False
    """
    def __init__(self, *linetypes):
        """
        Create a LineTypes object and match the given LineTypes
        >>> LineTypes(LineType.train, LineType.bus)
        """
        self._linetypes = set()
        for linetype in linetypes:
            if not isinstance(linetype, LineType):
                raise TypeError('expected LineType instance, got %s' % repr(linetype))
            self._linetypes |= set(linetype) | set(linetype.contained_in())

    def exclude(self, *linetypes):
        """
        Return a new LineTypes object with the given linetypes and their subtypes excluded.
        >>> LineTypes.any.exclude(LineType.train, Linetype.bus)  # Exclude all trains and buses
        """
        expanded = self._linetypes
        for linetype in linetypes:
            if not isinstance(linetype, LineType):
                raise TypeError('expected LineType instance, got %s' % repr(linetype))
            expanded -= set(linetype)

        r = LineTypes()
        r._linetypes = expanded
        return r

    def include(self, *linetypes):
        """
        Return a new LineTypes object with the given linetype and their parents and subtypes included.
        >>> LineTypes.none.include(LineType.train, Linetype.bus)  # Include all trains and buses
        """
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
