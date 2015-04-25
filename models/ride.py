#!/usr/bin/env python3
from .base import ModelBase
from .lines import Line
from .timeandplace import TimeAndPlace

class Ride(ModelBase):
    class StopPointer():
        def __init__(self, i: int):
            self._i = i

        def __int__(self):
            return self._i

        def __index__(self):
            return self._i

        def __repr__(self):
            return 'p:%d' % self._i

    class Segment():
        def __init__(self, ride, origin=None, destination=None):
            self.ride = ride
            self._pointer_origin = origin
            self._pointer_destination = destination

        @classmethod
        def load(cls, data):
            ride = Ride.unserialize(data['ride'])
            origin = data.get('origin', None)
            destination = data.get('destination', None)
            me = ride[origin:destination]
            obj = cls(ride, me._pointer_origin, me._pointer_destination)
            return obj

        def _stops(self):
            return self.ride._stops[self._pointer_origin:self._pointer_destination]

        @property
        def is_complete(self):
            return None not in self._stops()

        def __len__(self):
            return len(self._stops)

        def __getitem__(self, key):
            if isinstance(key, slice):
                if key.step is not None:
                    raise NotImplementedError('slicing a Ride.Segment with steps is not supported')
                if self._pointer_origin is not None:
                    if type(key.start) != int:
                        start = key.start
                    elif key.start >= 0:
                        start = int(self._pointer_origin)+key.start
                    else:
                        start = int(self._pointer_destination)+1-key.start
                    if type(key.stop) != int:
                        stop = key.stop
                    elif key.start >= 0:
                        stop = int(self._pointer_origin)+key.stop
                    else:
                        stop = int(self._pointer_destination)+1-key.stop
                else:
                    start, stop = key.start, key.stop
                return Ride.Segment(self.ride, start, stop)
            else:
                if type(key) != int:
                    return self.ride[key]
                else:
                    return self._stops()[key][1]

        def __iter__(self, key=None):
            for stop in self._stops():
                yield stop[1]

        def items(self, key):
            for stop in self._stops():
                yield stop

        @property
        def origin(self):
            return self.ride[0].stop

        @property
        def destination(self):
            return self.ride[-1].stop

        @property
        def departure(self):
            return self.ride[0].departure

        @property
        def arrival(self):
            return self.ride[-1].arrival

        def __getattr__(self, name):
            return getattr(self.ride, name)

        def __eq__(self, other):
            return (isinstance(other, Ride.Segment) and self.ride == other.ride and
                    self._pointer_origin == other._pointer_origin and
                    self._pointer_destination == other._pointer_destination)

        def serialize(self, ids):
            return ModelBase.serialize(self, ids)

        def _serialize(self, ids):
            data = {
                'ride': self.ride.serialize(ids)
            }
            if self._pointer_origin is not None:
                data['origin'] = int(self._pointer_origin)
            if self._pointer_destination is not None:
                data['destination'] = int(self._pointer_destination)
            return data


    def __init__(self, line: Line=None, number: str=None):
        super().__init__()
        self._stops = []
        self._paths = {}
        self.line = line
        self.number = number
        self.canceled = None
        self.bike_friendly = None
        self.infotexts = []

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'line')
        self._serial_get(data, 'number')
        self._serial_get(data, 'canceled')
        self._serial_get(data, 'bike_friendly')

        self._serial_get(data, 'stops')
        self._stops = [TimeAndPlace.unserialize(stop) for stop in self.stops]
        del self.stops

        self._serial_get(data, 'paths')
        self._paths = {tuple(self._stops[int(i)][0] for i in k.split(',')): [self.unserialize(p) for p in v] for k, v in self.paths}
        del self.paths

    @property
    def is_complete(self):
        return None not in self._stops

    def __len__(self):
        return len(self._stops)

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step is not None:
                raise NotImplementedError('slicing a Ride with steps is not supported')
            return Ride.Segment(self,
                               None if key.start is None else self._stops[int(key.start)][0],
                               None if key.stop is None else self._stops[int(key.stop)][0])
        else:
            return self._stops[int(key)][1]

    def __setitem__(self, key, item):
        assert isinstance(item, TimeAndPlace) or item is None
        self._stops[int(key)] = item

    def __delitem__(self, key):
        key = int(key)
        del self._stops[key]
        self._alter_pointers_after(key-1, -1)

    def __iter__(self, key):
        for stop in self._stops:
            yield stop[1]

    def items(self, key):
        for stop in self._stops:
            yield stop

    def _alter_pointers_after(self, pos: int, diff: int):
        for stop in self._stops[pos+1:]:
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

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, 'line', ids)
        self._serial_add(data, 'number', ids)
        self._serial_add(data, 'canceled', ids)
        self._serial_add(data, 'bike_friendly', ids)
        if self._stops:
            stops = [(stop[1].serialize(ids) if stop[1] is not None else None) for stop in self._stops]
            self._serial_add(data, 'stops', ids, val=stops)
        self._serial_add(data, 'paths', ids, val={('%d,%d' % k): [('tuple', p) for p in v] for k,v in self._paths.items()})
        return data
