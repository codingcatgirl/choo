from abc import ABC, abstractmethod
from collections import OrderedDict, namedtuple
from datetime import datetime, timedelta
from math import asin, cos, radians, sin, sqrt


class Serializable(ABC):
    subclasses = {}

    @classmethod
    def _collect_serializables(cls):
        cls.serialized_type_name = cls._get_serialized_type_name()
        cls.subclasses = {cls.serialized_type_name: cls} if cls.serialized_type_name is not None else {}
        for sc in cls.__subclasses__():
            cls.subclasses.update(sc._collect_serializables())
        return cls.subclasses

    @classmethod
    @abstractmethod
    def _get_serialized_type_name(cls):
        pass

    def serialize(self, by_reference=False, _id_lookup=None, **kwargs):
        if self.serialized_type_name is None:
            raise TypeError('Only subclasses of this class can be serialized.')

        if by_reference:
            from ..caches import DefaultCache
            cache = DefaultCache()
            cache.add_recursive(self)
            objects = cache.create_serialization_ids()
            _id_lookup = cache.get_serialization_id
            objects = tuple(o.serialize(_id_lookup=_id_lookup, **kwargs) for o in objects)
            return OrderedDict((
                ('@object', _id_lookup(self)),
                ('@references', objects),
            ))

        result = OrderedDict({
            '@type': self.serialized_type_name,
        })
        result.update(self._serialize(_id_lookup=_id_lookup, **kwargs))
        return result

    @classmethod
    def unserialize(cls, data):
        data = data.copy()
        type_ = data.pop('@type')
        class_ = cls.subclasses.get(type_)
        if class_ is None:
            raise ValueError('Expected @type to be %s subclass, not %s' % (cls.__name__, type_))
        return class_._unserialize(data)

    @abstractmethod
    def _serialize(self):
        pass

    @classmethod
    @abstractmethod
    def _unserialize(cls, data):
        pass


class SimpleSerializable(Serializable, ABC):
    @classmethod
    def unserialize(cls, data):
        if isinstance(data, (dict, OrderedDict)) and '@type' in data:
            return super().unserialize(data)
        return cls._simple_unserialize(data)

    def serialize(self, simple=True, **kwargs):
        if self.serialized_type_name is None:
            raise TypeError('Only subclasses of this class can be serialized.')

        return self._simple_serialize() if simple else super().serialize(**kwargs)

    def _serialize(self, **kwargs):
        return {'value': self._simple_serialize()}

    @classmethod
    def _unserialize(cls, data):
        return cls._simple_unserialize(data['value'])

    @abstractmethod
    def _simple_serialize(self):
        pass

    @classmethod
    @abstractmethod
    def _simple_unserialize(cls, data):
        pass


class Coordinates(SimpleSerializable, namedtuple('Coordinates', ('lat', 'lon'))):
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

    @classmethod
    def _get_serialized_type_name(cls):
        return 'coordinates'

    def _simple_serialize(self):
        return [self.lat, self.lon]

    @classmethod
    def _simple_unserialize(cls, data):
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
