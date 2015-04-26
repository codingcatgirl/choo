#!/usr/bin/env python3
from .base import ModelBase, Serializable
from .location import Location
from .linetypes import LineType, LineTypes
from .realtime import RealtimeTime

class Stop(Location):
    # defined at the end of file
    #_validate = {
    #    'rides': (None, (Ride.Segment, )),
    #    'lines': (None, (Line, ))
    #}
    
    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)
        self.rides = []
        self.lines = []

    def _serialize(self, depth):
        data = {}
        if self.rides is not None:
            data['rides'] = [ride.serialize() for ride in self.rides]
        if self.lines is not None:
            data['lines'] = [line.serialize() for line in self.lines]
        return data
        
    def _unserialize(self, data):
        self._serial_get(data, 'country')
        self._serial_get(data, 'city')
        self._serial_get(data, 'name')
        if 'rides' in data:
            self.rides = [Ride.Segment.unserialize(ride) for ride in data['rides']]
        if 'lines' in data:
            self.lines = [Line.unserialize(line) for line in data['lines']]

    def __repr__(self):
        return '<%s %s, %s>' % ('Stop', self.city, self.name)

    def __eq__(self, other):
        if not isinstance(other, Stop):
            return None
        for k, id_ in self._ids.items():
            if id_ is not None and other._ids.get(k) == id_:
                return True
        if self.coords is not None and self.coords == other.coords:
            return True
        return self.name is not None and self.name == other.name and self.city == other.city and self.country == other.country

    def _serialize(self, ids):
        data = {}
        if self.rides:
            rides = [ride.serialize(ids) for ride in self.rides]
            if rides.count({}) == len(rides):
                rides = []
            self._serial_add(data, 'rides', ids, val=rides)

        if self.lines:
            lines = [line.serialize(ids) for line in self.lines]
            if lines.count({}) == len(lines):
                lines = []
            self._serial_add(data, 'lines', ids, val=lines)
        return data


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
    def __init__(self, stop=None, platform=None, arrival=None, departure=None, coords: tuple=None):
        super().__init__()
        self.stop = stop
        self.platform = platform
        self.coords = coords
        self.arrival = arrival
        self.departure = departure

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'stop')
        self._serial_get(data, 'platform')
        self._serial_get(data, 'coords')
        self._serial_get(data, 'arrival')
        self._serial_get(data, 'departure')

    def __eq__(self, other):
        return (isinstance(other, TimeAndPlace) and self.stop == other.stop and
                self.platform == other.platform and self.arrival == other.arrival and
                self.departure == other.departure)

    def __repr__(self):
        return '<TimeAndPlace %s %s %s %s>' % (repr(self.arrival), repr(self.departure), repr(self.stop), repr(self.platform))

    def _serialize(self, ids):
        data = super()._serialize(ids)
        self._serial_add(data, 'stop', ids)
        self._serial_add(data, 'platform', ids)
        self._serial_add(data, 'coords', ids)
        self._serial_add(data, 'arrival', ids)
        self._serial_add(data, 'departure', ids)
        return data


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
        
        
class Trip(ModelBase):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.walk_speed = 'normal'

    class Request(ModelBase):
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

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'walk_speed')
        self._serial_get(data, 'parts')
        self.parts = [ModelBase.unserialize(part) for part in self.parts]

    def _serialize(self, ids):
        data = {}
        parts = [part.serialize(ids) for part in self.parts]
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
            if isinstance(part, RideSegment):
                return None if part.departure is None else part.departure - delta
            elif part.duration is None:
                return None
            else:
                delta += part.duration

    @property
    def arrival(self):
        delta = timedelta(0)
        for part in reversed(self.parts):
            if isinstance(part, RideSegment):
                return None if part.arrival is None else part.arrival + delta
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
        return max(0, len([part for part in self.parts if isinstance(part, RideSegment)])-1)

    @property
    def bike_friendly(self):
        tmp = [part.bike_friendly for part in self.parts if isinstance(part, RideSegment)]
        if False in tmp:
            return False
        if None in tmp:
            return None
        return True

    def to_request(self):
        r = TripRequest()
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