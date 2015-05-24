#!/usr/bin/env python3
from .base import ModelBase, Serializable, TripPart
from .locations import Coordinates
from .timeandplace import TimeAndPlace
from .line import Line


class Ride(ModelBase):
    _serialize_depth = 3

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
        return {
            'line': (None, Line),
            'number': (None, str),
            'direction': (None, str),
            'canceled': (None, bool),
            'bike_friendly': (None, bool),
            'infotexts': ((str, ), )
        }

    def _serialize(self, depth):
        data = {}
        self._serial_add(data, 'number')
        self._serial_add(data, 'direction')
        self._serial_add(data, 'canceled')
        self._serial_add(data, 'bike_friendly')
        if self.infotexts:
            data['infotexts'] = self.infotexts
        data['stops'] = []
        for pointer, stop in self._stops:
            data['stops'].append(stop.serialize(depth) if stop else None)
        data['paths'] = {int(i): [p.serialize() for p in path] for i, path in self._paths.items()}
        if self.line:
            data['line'] = self.line.serialize(depth)
        return data

    def _unserialize(self, data):
        self._serial_get(data, 'number')
        self._serial_get(data, 'direction')
        self._serial_get(data, 'canceled')
        self._serial_get(data, 'bike_friendly')
        self.infotexts = data['infotexts'] if 'infotexts' in data else []
        for s in data['stops']:
            self.append(TimeAndPlace.unserialize(s) if s is not None else None)
        for i, path in data['paths'].items():
            self._paths[self._stops[i][0]] = [Coordinates.unserialize(p) for p in path]
        if 'line' in data:
            self.line = Line.unserialize(data['line'])

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
        self._stops.prepend((pointer, item))
        self._alter_pointers_after(0, 1)
        return pointer

    def insert(self, position, item):
        assert isinstance(item, TimeAndPlace) or item is None
        position = max(0, min(position, len(self._stops)))
        pointer = Ride.StopPointer(position)
        self._stops.insert(position, (pointer, item))
        self._alter_pointers_after(position, 1)
        return pointer

    def extend(self, item):
        pass  # todo

    def __eq__(self, other):
        pass  # todo

    class StopPointer():
        def __init__(self, i: int):
            self._i = i

        def __int__(self):
            return self._i

        def __index__(self):
            return self._i

        def __repr__(self):
            return 'p:%d' % self._i


class RideSegment(TripPart):
    def __init__(self, ride=None, origin=None, destination=None):
        self.ride = ride
        self._origin = origin
        self._destination = destination

    @classmethod
    def _validate(cls):
        return {
            'ride': Ride,
            '_origin': (None, Ride.StopPointer),
            '_destination': (None, Ride.StopPointer)
        }

    def _serialize(self, depth):
        data = {}
        data['ride'] = self.ride.serialize(depth)
        if self._origin:
            data['origin'] = int(self._origin)
        if self._destination:
            data['destination'] = int(self._destination)
        return data

    def _unserialize(self, data):
        self.ride = Ride.unserialize(data['ride'])
        if 'origin' in data:
            self._origin = self.ride.pointer(data['origin'])
        if 'destination' in data:
            self._destination = self.ride.pointer(data['destination'])

    def _stops(self):
        return self.ride._stops[self._origin:int(self._destination)+1]

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
        assert isinstance(other, RideSegment)
        return (self.ride == other.ride and
                self._origin == other._origin and
                self._destination == other._destination)
