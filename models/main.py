#!/usr/bin/env python3
from .base import ModelBase, Serializable
from .location import Coordinates, Location, Way
from .linetypes import LineType, LineTypes
from .realtime import RealtimeTime
from datetime import timedelta


class Stop(Location):
    # defined at the end of file
    # _validate = {
    #     'rides': (None, (Ride.Segment, )),
    #     'lines': (None, (Line, ))
    # }

    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)
        self.rides = []
        self.lines = []

    def _serialize(self, depth):
        data = {}
        if self.rides is not None:
            data['rides'] = [ride.serialize(depth) for ride in self.rides]
        if self.lines is not None:
            data['lines'] = [line.serialize(depth) for line in self.lines]
        return data

    def _unserialize(self, data):
        self._serial_get(data, 'country')
        self._serial_get(data, 'city')
        self._serial_get(data, 'name')
        if 'rides' in data:
            self.rides = [Ride.Segment.unserialize(r) for r in data['rides']]
        if 'lines' in data:
            self.lines = [Line.unserialize(line) for line in data['lines']]

    def __repr__(self):
        return '<%s %s, %s>' % ('Stop', self.city, self.name)

    def __eq__(self, other):
        assert isinstance(other, Stop)
        for k, id_ in self._ids.items():
            if id_ is not None and other._ids.get(k) == id_:
                return True
        if self.coords is not None and self.coords == other.coords:
            return True
        return (self.name is not None and self.name == other.name and
                self.city == other.city and self.country == other.country)


class Line(ModelBase):
    _validate = {
        'linetype': (None, LineType),
        'product': (None, str),
        'name': (None, str),
        'shortname': (None, str),
        'route': (None, str),
        'first_stop': (None, Stop),
        'last_stop': (None, Stop),
        'network': (None, str),
        'operator': (None, str)
    }

    def __init__(self, linetype: LineType=None):
        super().__init__()
        self.linetype = linetype
        self.product = None
        self.name = None
        self.shortname = None
        self.route = None
        self.first_stop = None
        self.last_stop = None

        self.network = None
        self.operator = None

    def _serialize(self, depth):
        data = {}
        self._serial_add(data, 'product')
        self._serial_add(data, 'name')
        self._serial_add(data, 'shortname')
        self._serial_add(data, 'route')
        self._serial_add(data, 'network')
        self._serial_add(data, 'operator')
        if self.linetype:
            data['linetype'] = self.linetype.serialize()
        if self.first_stop:
            data['first_stop'] = self.first_stop.serialize(depth)
        if self.last_stop:
            data['last_stop'] = self.last_stop.serialize(depth)
        return data

    def _unserialize(self, data):
        self._serial_get(data, 'product')
        self._serial_get(data, 'name')
        self._serial_get(data, 'shortname')
        self._serial_get(data, 'route')
        self._serial_get(data, 'network')
        self._serial_get(data, 'operator')
        if 'linetype' in data:
            self.linetype = LineType.unserialize(data['linetype'])
        if 'first_stop' in data:
            self.first_stop = Stop.unserialize(data['first_stop'])
        if 'last_stop' in data:
            self.last_stop = Stop.unserialize(data['last_stop'])


class TimeAndPlace(ModelBase):
    _validate = {
        'stop': Stop,
        'platform': (None, str),
        'coords': (None, Coordinates),
        'arrival': (None, RealtimeTime),
        'departure': (None, RealtimeTime)
    }

    def __init__(self, stop=None, platform=None, arrival=None, departure=None, coords=None):
        super().__init__()
        self.stop = stop
        self.platform = platform
        self.coords = coords
        self.arrival = arrival
        self.departure = departure

    def _serialize(self, depth):
        data = {}
        self._serial_add(data, 'platform')
        data['stop'] = self.stop.serialize(depth)
        if self.coords:
            data['coords'] = self.coords.serialize()
        if self.arrival:
            data['arrival'] = self.arrival.serialize()
        if self.departure:
            data['departure'] = self.departure.serialize()
        return data

    def _unserialize(self, data):
        self._serial_get(data, 'platform')
        self.stop = Stop.unserialize(data['stop'])
        if 'coords' in data:
            self.coords = Coordinates.unserialize(data['coords'])
        if 'arrival' in data:
            self.arrival = RealtimeTime.unserialize(data['arrival'])
        if 'departure' in data:
            self.departure = RealtimeTime.unserialize(data['departure'])

    def __eq__(self, other):
        assert isinstance(other, TimeAndPlace)
        return (self.stop == other.stop and
                self.platform == other.platform and
                self.arrival == other.arrival and
                self.departure == other.departure)

    def __repr__(self):
        return ('<TimeAndPlace %s %s %s %s>' %
                (self.arrival, self.departure, repr(self.stop), self.platform))


class Ride(ModelBase):
    _validate = {
        # '_stop': ((None, TimeAndPlace), ),
        # '_paths': (None, str),
        'line': (None, Line),
        'number': (None, str),
        'canceled': (None, bool),
        'bike_friendly': (None, bool),
        'infotexts': ((str, ), )
    }

    _serialize_depth = 3

    def __init__(self, line: Line=None, number: str=None):
        super().__init__()
        self._stops = []
        self._paths = {}
        self.line = line
        self.number = number
        self.canceled = None
        self.bike_friendly = None
        self.infotexts = []

    def _serialize(self, depth):
        data = {}
        self._serial_add(data, 'number')
        self._serial_add(data, 'canceled')
        self._serial_add(data, 'bike_friendly')
        if self.infotexts:
            data['infotexts'] = self.infotexts
        data['stops'] = []
        for pointer, stop in self._stops:
            data['stops'].append(stop.serialize(depth) if stop else None)
        # data['paths'] =  #todo
        if self.line:
            data['line'] = self.line.serialize(depth)
        return data

    def _unserialize(self, data):
        self._serial_get(data, 'number')
        self._serial_get(data, 'canceled')
        self._serial_get(data, 'bike_friendly')
        self.infotexts = data['infotexts'] if 'infotexts' in data else []
        for s in data['stops']:
            self.append(TimeAndPlace.unserialize(s) if s is not None else None)
        # self.paths #todo
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
            return Ride.Segment(self,
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

    class Segment(Serializable):
        # defined at the end of file
        # _validate = {
        #     'ride': Ride,
        #     '_pointer_origin': (None, Ride.StopPointer),
        #     '_pointer_destination': (None, Ride.StopPointer)
        # }

        def __init__(self, ride=None, origin=None, destination=None):
            self.ride = ride
            self._origin = origin
            self._destination = destination

        def _serialize(self, depth):
            data = {}
            data['ride'] = self.ride.serialize(depth)
            if self._origin:
                data['origin'] = int(self._origin)
            if self._destination:
                data['destination'] = int(self._destination) - 1
            return data

        def _unserialize(self, data):
            self.ride = Ride.unserialize(data['ride'])
            if 'origin' in data:
                self._origin = self.ride.pointer(data['origin'])
            if 'destination' in data:
                self._destination = self.ride.pointer(data['destination'] + 1)

        def _stops(self):
            return self.ride._stops[self._origin:self._destination]

        @property
        def is_complete(self):
            return None not in self._stops()

        def __len__(self):
            return len(self._stops)

        def __getitem__(self, key):
            if isinstance(key, slice):
                if key.step is not None:
                    raise TypeError('Ride.Segment cannot be slices with steps')
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
            assert isinstance(other, Ride.Segment)
            return (self.ride == other.ride and
                    self._origin == other._origin and
                    self._destination == other._destination)
Ride.Segment.Model = Ride

class Trip(ModelBase):
    _validate = {
        'parts': ((Ride.Segment, Way), ),
        'walk_speed': str
    }

    def __init__(self):
        super().__init__()
        self.parts = []
        self.walk_speed = 'normal'

    def _serialize(self, depth):
        data = {}
        data['parts'] = [p.serialize(depth, True) for p in self.parts]
        return data

    def _unserialize(self, data):
        self.parts = [self._unserialize_typed(part, (Ride.Segment, Way))
                      for model, part in data['parts']]

    class Request(ModelBase.Request):
        def __init__(self):
            super().__init__()
            self.parts = []
            self.walk_speed = 'normal'
            self.origin = None
            self.destination = None
            self.departure = None
            self.arrival = None
            self.linetypes = LineTypes()
            self.max_changes = None
            self.bike_friendly = None

        def _load(self, data):
            super()._load(data)
            self._serial_get(data, 'walk_speed')
            self._serial_get(data, 'parts')
            self.parts = [ModelBase.unserialize(part) for part in self.parts]

        def _serialize(self, ids):
            data = {}
            parts = [part.serialize() for part in self.parts]
            self._serial_add(data, 'parts', ids, val=parts)
            self._serial_add(data, 'walk_speed', ids)
            return data

    @property
    def origin(self):
        return self.parts[0].origin

    @property
    def destination(self):
        return self.parts[-1].destination

    @property
    def departure(self):
        delta = timedelta(0)
        for part in self.parts:
            if isinstance(part, Ride.Segment):
                return (part.departure - delta) if part.departure else None
            elif part.duration is None:
                return None
            else:
                delta += part.duration

    @property
    def arrival(self):
        delta = timedelta(0)
        for part in reversed(self.parts):
            if isinstance(part, Ride.Segment):
                return (part.arrival + delta) if part.arrival else None
            elif part.duration is None:
                return None
            else:
                delta += part.duration

    @property
    def linetypes(self):
        types = LineTypes(False)
        for part in self.parts:
            linetype = part.line.linetype
            if linetype is not None:
                types.add(linetype)
        return types

    @property
    def changes(self):
        changes = -1
        for part in self.parts:
            if isinstance(part, Ride.Segment):
                changes += 1
        return max(0, changes)

    @property
    def bike_friendly(self):
        for part in self.parts:
            if not isinstance(part, Ride.Segment):
                continue
            if part.bike_friendly is None:
                return None
            elif part.bike_friendly is False:
                return False
        return True

    def to_request(self):
        r = Trip.Request()
        r.walk_speed = self.walk_speed
        r.origin = self.origin
        r.destination = self.destination
        r.departure = self.departure
        r.arrival = self.arrival
        r.linetypes = self.linetypes
        r.max_changtes = self.max_changes
        r.bike_friendly = self.bike_friendly
        return r


Stop._validate = {
    'rides': (None, (Ride.Segment, )),
    'lines': (None, (Line, ))
}
Ride.Segment._validate = {
    'ride': Ride,
    '_origin': (None, Ride.StopPointer),
    '_destination': (None, Ride.StopPointer)
}
