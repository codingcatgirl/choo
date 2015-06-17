#!/usr/bin/env python3
from .base import Collectable, TripPart
from .locations import Coordinates
from .timeandplace import TimeAndPlace
from .line import Line


class Ride(Collectable):
    def __init__(self, line=None, number=None):
        super().__init__()
        self._stops = []
        self._paths = {}
        self.line = line
        self.number = number
        self.direction = None
        self.canceled = None
        self.bike_friendly = None
        self.infotexts = []

    @classmethod
    def _validate(cls):
        return (
            ('line', (None, Line)),
            ('number', (None, str)),
            ('direction', (None, str)),
            ('canceled', (None, bool)),
            ('bike_friendly', (None, bool)),
            ('infotexts', None),
            ('_stops', None),
            ('_paths', None),
        )

    _update_default = ('line', 'number', 'direction', 'canceled', 'bike_friendly', 'infotexts')

    def _update(self, other, better):
        # todo: stops, paths
        pass

    def _validate_custom(self, name, value):
        if name == 'infotexts':
            for v in value:
                if not isinstance(v, str):
                    return False
            return True
        elif name == '_stops':
            for v in value:
                if type(v) != tuple or len(v) != 2:
                    return False

                if not isinstance(v[0], self.__class__.StopPointer):
                    return False

                if v[1] is not None and not isinstance(v[1], TimeAndPlace):
                    return False
            return True
        elif name == '_paths':
            if not isinstance(value, dict):
                return False
            for k, v in value.items():
                if not isinstance(k, self.__class__.StopPointer):
                    return False

                try:
                    v = list(v)
                except:
                    return False
                for i in v:
                    if not isinstance(i, Coordinates):
                        return False
            return True

    def _serialize_custom(self, name):
        if name == 'infotexts':
            return 'infotexts', (self.infotexts if self.infotexts else None)
        elif name == '_stops':
            return 'stops', [(s.serialize() if s else None) for i, s in self._stops]
        elif name == '_paths':
            return 'paths', {int(i): [p.serialize() for p in path] for i, path in self._paths.items()}

    def _unserialize_custom(self, name, data):
        if name == 'infotexts':
            self.infotexts = data
        elif name == 'stops':
            for s in data:
                self.append(TimeAndPlace.unserialize(s) if s is not None else None)
        elif name == 'paths':
            for i, path in data.items():
                self._paths[self._stops[i][0]] = [Coordinates.unserialize(p) for p in path]

    def _collect_children(self, collection, last_update=None):
        super()._collect_children(collection, last_update)

        if self.line is not None:
            self.line._update_collect(collection, last_update)

        for stop in self._stops:
            if stop[1] is not None:
                stop[1]._update_collect(collection, last_update)

    @property
    def is_complete(self):
        return None not in self._stops

    def pointer(self, i):
        return self._stops[int(i)][0]

    def __len__(self):
        return len(self._stops)

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step is not None:
                raise TypeError('Ride cannot be sliced with steps')
            return RideSegment(self,
                               self.pointer(key.start) if key.start else None,
                               self.pointer(key.stop) if key.stop else None)
        else:
            return self._stops[int(key)][1]

    def __setitem__(self, key, item):
        assert isinstance(item, TimeAndPlace) or item is None
        self._stops[int(key)][1] = item

    def __delitem__(self, key):
        key = int(key)
        del self._stops[key]
        self._alter_pointers_after(key - 1, -1)

    def __iter__(self, key):
        for stop in self._stops:
            yield stop[1]

    def items(self, key):
        for stop in self._stops:
            yield stop

    def _alter_pointers_after(self, pos: int, diff: int):
        for stop in self._stops[pos + 1:]:
            stop[0]._i += diff

    def append(self, item):
        assert isinstance(item, TimeAndPlace) or item is None
        pointer = Ride.StopPointer(len(self._stops))
        self._stops.append((pointer, item))
        return pointer

    def prepend(self, item):
        assert isinstance(item, TimeAndPlace) or item is None
        pointer = Ride.StopPointer(0)
        self._stops.insert(0, (pointer, item))
        self._alter_pointers_after(0, 1)
        return pointer

    def insert(self, position, item):
        assert isinstance(item, TimeAndPlace) or item is None
        position = max(0, min(position, len(self._stops)))
        pointer = Ride.StopPointer(position)
        self._stops.insert(position, (pointer, item))
        self._alter_pointers_after(position, 1)
        return pointer

    def __eq__(self, other):
        if not isinstance(other, Ride):
            return False

        byid = self._equal_by_id(other)
        if byid is False:
            return False

        if byid is None:
            if self.number is not None and other.number is not None and self.number != other.number:
                return False

            if self[-1] is not None and other[-1] is not None and self[-1].stop != other[-1].stop:
                return False

            if self[0] is not None and other[0] is not None and self[0].stop != other[0].stop:
                return False

        for stop in self._stops[1:-1]:
            if stop[1] is None:
                continue
            for stop2 in other._stops[1:-1]:
                if stop2[1] is None:
                    continue
                if stop[1] == stop2[1]:
                    return True

        return False

    def __repr__(self):
        return '<Ride %s %s>' % (self.number, repr(self.line))

    class StopPointer():
        def __init__(self, i: int):
            self._i = i

        @classmethod
        def _validate(cls):
            return (
                ('_i', int),
            )

        def _serialize(self):
            return self._i

        def __int__(self):
            return self._i

        def __index__(self):
            return self._i

        def __repr__(self):
            return 'p:%d' % self._i

    class Request(Collectable.Request):
        pass

    class Results(Collectable.Results):
        def __init__(self, results=[], scored=False):
            self.content = RideSegment
            super().__init__(results, scored)


class RideSegment(TripPart):
    def __init__(self, ride=None, origin=None, destination=None):
        self.ride = ride
        self._origin = origin
        self._destination = destination

    @classmethod
    def _validate(cls):
        return (
            ('ride', Ride),
            ('_origin', None),
            ('_destination', None),
        )

    def _validate_custom(self, name, value):
        if name in ('_origin', '_destination'):
            return value is None or isinstance(value, Ride.StopPointer)

    def _serialize_custom(self, name):
        if name == '_origin':
            return 'origin', int(self._origin) if self._origin is not None else None
        elif name == '_destination':
            return 'destination', int(self._destination) if self._destination is not None else None

    def _unserialize_custom(self, name, data):
        if name == 'origin':
            self._origin = self.ride.pointer(data)
        elif name == 'destination':
            self._destination = self.ride.pointer(data)

    def _stops(self):
        if self._destination is None:
            return self.ride._stops[self._origin:None]
        else:
            return self.ride._stops[self._origin:int(self._destination) + 1]

    @property
    def is_complete(self):
        return None not in self._stops()

    def __len__(self):
        return len(self._stops)

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step is not None:
                raise TypeError('RideSegment cannot be slices with steps')
            if self._origin is not None:
                if type(key.start) != int:
                    start = key.start
                elif key.start >= 0:
                    start = int(self._origin) + key.start
                else:
                    start = int(self._destination) + 1 - key.start
                if type(key.stop) != int:
                    stop = key.stop
                elif key.start >= 0:
                    stop = int(self._origin) + key.stop
                else:
                    stop = int(self._destination) + 1 - key.stop
            else:
                start, stop = key.start, key.stop
            return RideSegment(self.ride, start, stop)
        else:
            if type(key) != int:
                return self.ride[key]
            else:
                return self._stops()[key][1]

    def __iter__(self, key=None):
        for stop in self._stops():
            yield stop[1]

    def items(self):
        for stop in self._stops():
            yield stop

    @property
    def origin(self):
        return self[0].stop

    @property
    def destination(self):
        return self[-1].stop

    @property
    def departure(self):
        return self[0].departure

    @property
    def arrival(self):
        return self[-1].arrival

    def __getattr__(self, name):
        return getattr(self.ride, name)

    def __eq__(self, other):
        if not isinstance(other, RideSegment):
            return False

        if self.ride is other.ride:
            return self._origin == other._origin and self._destination == other._destination
        elif self.ride == other.ride:
            return (self.origin == other.origin and self.departure == other.departure and
                    self.destination == other.destination and self.arrival == other.arrival)
        return False

    def __repr__(self):
        return '<RideSegment %s %s %s>' % (repr(self.origin), repr(self.destination), repr(self.ride))
