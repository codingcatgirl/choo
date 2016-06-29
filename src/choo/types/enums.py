from enum import Enum

from .misc import SimpleSerializable


class SerializableEnumMixin:
    def _simple_serialize(self):
        return self.name

    @classmethod
    def _simple_unserialize(cls, data):
        result = getattr(cls, data)
        if not isinstance(result, cls):
            raise AttributeError
        return result

SimpleSerializable.register(SerializableEnumMixin)


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

    def __repr__(self):
        return 'POIType.' + self.name


class PlatformType(SerializableEnumMixin, Enum):
    unknown = 'unknown'
    street = 'street'
    platform = 'platform'

    def __repr__(self):
        return 'PlatformType.' + self.name


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
        >>> LineTypes.any.exclude(LineType.train, LineType.bus)  # Exclude all trains and buses
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
        >>> LineTypes.none.include(LineType.train, LineType.bus)  # Include all trains and buses
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
        if not isinstance(linetype, LineType):
            raise TypeError('can only match LineType instances')
        return linetype in self._linetypes

    def __repr__(self):
        return 'LineTypes(%s)' % ', '.join(str(lt) for lt in self)

LineTypes.any = LineTypes(LineType.any)
LineTypes.none = LineTypes()
