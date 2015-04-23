#!/usr/bin/env python3
from datetime import datetime, timedelta

class ModelBase():
    def __init__(self):
        self._ids = {}
        self._raws = {}

    @classmethod
    def load(cls, data):
        obj = cls()
        obj._load(data)
        return obj

    def _load(self, data):
        self._serial_get(data, '_ids')
        self._serial_get(data, '_raws')

    @classmethod
    def unserialize(cls, data):
        if data is None:
            return None
        if type(data) not in (list, tuple):
            return data
        mytype, data = data
        if mytype is None:
            return data
        elif mytype == 'datetime':
            return datetime.strptime(data, '%Y-%m-%d %H:%M')
        elif mytype == 'timedelta':
            return timedelta(seconds=data)
        elif mytype == 'tuple':
            return tuple(data)
        elif mytype == 'list':
            return data
        else:
            return globals()[mytype].load(data)

    def serialize(self, ids=None):
        if ids is None:
            ids = []
        myid = id(self)
        if len(ids) != len(set(ids)):
            return {}
        data = {}
        classes = self.__class__.__mro__
        newids = ids+[myid]
        for oneclass in classes:
            if hasattr(oneclass, '_serialize'):
                olddata = data
                newdata = oneclass._serialize(self, newids)
                if type(newdata) != dict and not data:
                    data = newdata
                    break
                data = newdata
                data.update(olddata)

        if myid in ids:
            data['is_truncated'] = True
        return (self.__class__.__name__, data)

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, '_ids', ids)
        if 'noraws' not in ids:
            self._serial_add(data, '_raws', ids)
        return data

    def _serial_add(self, data, name, ids, **kwargs):
        if 'val' in kwargs:
            val = kwargs['val']
        else:
            val = getattr(self, name)
            if val is None:
                return
        if isinstance(val, ModelBase):
            data[name] = val.serialize(ids)
        elif isinstance(val, datetime):
            data[name] = ('datetime', val.strftime('%Y-%m-%d %H:%M'))
        elif isinstance(val, timedelta):
            data[name] = ('timedelta', val.total_seconds())
        elif type(val) == list:
            data[name] = ('list', val)
        elif type(val) == tuple:
            data[name] = ('tuple', val)
        else:
            data[name] = val

    def _serial_get(self, data, name):
        if name in data:
            setattr(self, name, ModelBase.unserialize(data[name]))


class SearchResults():
    def __init__(self, results=[], subject=None, api=None, method=None):
        self.subject = subject
        self.api = api
        self.method = method
        self.results = tuple(results)

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'results')
        results = self.results
        self.results = []
        for result in results:
            if type(result) in (tuple, list):
                self.results.append((ModelBase.unserialize(result[0]), result[1]))
            else:
                self.results.append(ModelBase.unserialize(result))
        self._serial_get(data, 'subject')
        self._serial_get(data, 'api')
        self._serial_get(data, 'method')

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, 'subject', ids)
        self._serial_add(data, 'api', ids)
        self._serial_add(data, 'method', ids)
        if type(self.results[0]) == tuple:
            results = [(item[0].serialize(ids), item[1]) for item in self.results]
        else:
            results = [item.serialize(ids) for item in self.results]
        self._serial_add(data, 'results', ids, val=results)
        return data

    def __iter__(self):
        for result in self.results:
            yield result

    def __getitem__(self, key):
        return self.results[key]


class Location(ModelBase):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        self.country = country
        self.city = city
        self.name = name
        self.coords = coords

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'country')
        self._serial_get(data, 'city')
        self._serial_get(data, 'name')
        self._serial_get(data, 'coords')

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, 'country', ids,)
        self._serial_add(data, 'city', ids)
        self._serial_add(data, 'name', ids)
        self._serial_add(data, 'coords', ids)
        return data


class Stop(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)
        self.rides = []
        self.lines = []

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'rides')
        self._serial_get(data, 'lines')
        self.rides = [ModelBase.unserialize(ride) for ride in self.rides]
        self.lines = [ModelBase.unserialize(line) for line in self.lines]

    def __repr__(self):
        return '<%s %s, %s>' % ('Stop', self.city, self.name)

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


class POI(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)

    def _serialize(self, ids):
        return {}


class Address(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)

    def _serialize(self, ids):
        return {}


class RealtimeTime(ModelBase):
    def __init__(self, time: datetime, delay: timedelta=None, livetime: datetime=None):
        super().__init__()
        if livetime is not None:
            if delay is not None:
                assert livetime-time == delay
            else:
                delay = livetime-time

        self.time = time
        self.delay = delay

    @classmethod
    def load(cls, data):
        time = ModelBase.unserialize(data.get('time', None))
        delay = ModelBase.unserialize(data.get('delay', None))
        livetime = ModelBase.unserialize(data.get('livetime', None))
        obj = cls(time, delay, livetime)
        obj._load(data)
        return obj

    def __repr__(self):
        return '<RealtimeTime %s%s>' % (str(self.time)[:-3], (' +%d' % (self.delay.total_seconds()/60)) if self.delay is not None else '')

    @property
    def is_live(self):
        return self.delay is not None

    @property
    def livetime(self):
        if self.delay is not None:
            return self.time+self.delay
        else:
            return self.time

    def __add__(self, other):
        assert isinstance(other, timedelta)
        self.time += other

    def __sub__(self, other):
        assert isinstance(other, timedelta)
        self.time -= other

    def __eq__(self, other):
        return self.time == other.time

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, 'time', ids)
        self._serial_add(data, 'delay', ids)
        return data


class TimeAndPlace(ModelBase):
    def __init__(self, stop: Stop=None, platform: str=None, arrival: RealtimeTime=None, departure: RealtimeTime=None, coords: tuple=None):
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


class LineTypes(ModelBase):
    _known = ('localtrain', 'longdistance', 'highspeed', 'urban', 'metro', 'tram',
              'citybus', 'regionalbus', 'expressbus', 'suspended', 'ship', 'dialable',
              'other', 'walk')
    _shortcuts = {
        'bus': ('citybus', 'regionalbus', 'expressbus', 'dialbus'),
        'dial': ('dialbus', 'dialtaxi')
    }

    def __init__(self, all_types: bool=True):
        super().__init__()
        self._included = set(self._known) if all_types else set()

    @classmethod
    def load(cls, data):
        obj = cls()
        obj._included = data
        return obj

    def add(self, *args: str):
        for name in args:
            if name in self._known:
                self._included.add(name)
            elif name in self._shortcuts:
                for child in self._shortcuts[name]:
                    self._included.add(child)
            else:
                raise AttributeError('unsupported linetype: %s' % repr(name))

    def remove(self, *args: str):
        for name in args:
            if name in self._known:
                self._included.discard(name)
            elif name in self._shortcuts:
                for child in self._shortcuts[name]:
                    self._included.discard(child)
            else:
                raise AttributeError('unsupported linetype: %s' % repr(name))

    def __contains__(self, name: str):
        if type(name) == str:
            if name in self._known:
                return name in self._included
            elif name in self._shortcuts:
                return False not in [child in self._included for child in self._shortcuts[name]]
            else:
                raise AttributeError('unsupported linetype')
        else:
            for child in name:
                if name not in self._included:
                    return False
            return True

    def __nonzero__(self):
        return bool(self._included)

    def __eq__(self, other):
        return (isinstance(other, LineTypes) and self._incluced == other._included)

    def _serialize(self, ids):
        return self._included


class LineType(ModelBase):
    def __init__(self, name: str):
        super().__init__()
        if name in LineTypes._known:
            self.name = name
        else:
            raise AttributeError('unsupported linetype')

    @classmethod
    def load(cls, data):
        obj = cls(data)
        return obj

    def __eq__(self, name: str):
        if self.name == name or (name in LineTypes._shortcuts and self.name in LineTypes._shortcuts[name]):
            return True
        elif name in LineTypes._known:
            return False
        else:
            raise AttributeError('unsupported linetype')

    def _serialize(self, ids):
        return self.name


class Line(ModelBase):
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

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'linetype')
        self._serial_get(data, 'product')
        self._serial_get(data, 'name')
        self._serial_get(data, 'shortname')
        self._serial_get(data, 'route')
        self._serial_get(data, 'first_stop')
        self._serial_get(data, 'last_stop')
        self._serial_get(data, 'network')
        self._serial_get(data, 'operator')

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, 'linetype', ids)
        self._serial_add(data, 'product', ids)
        self._serial_add(data, 'name', ids)
        self._serial_add(data, 'shortname', ids)
        self._serial_add(data, 'route', ids)
        self._serial_add(data, 'first_stop', ids)
        self._serial_add(data, 'last_stop', ids)
        self._serial_add(data, 'network', ids)
        self._serial_add(data, 'operator', ids)
        return data


class Ride(ModelBase):
    def __init__(self, line: Line=None, number: str=None):
        super().__init__()
        self._stops = []
        self.line = line
        self.number = number
        self.bike_friendly = None

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'line')
        self._serial_get(data, 'number')
        self._serial_get(data, 'bike_friendly')
        self.stops = []
        self._serial_get(data, 'stops')
        self._stops = [TimeAndPlace.unserialize(stop) for stop in self.stops]
        del self.stops

    @property
    def is_complete(self):
        return None not in self._stops

    def __len__(self):
        return len(self._stops)

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step is not None:
                raise NotImplementedError('slicing a Ride with steps is not supported')
            return RideSegment(self,
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
        pointer = RideStopPointer(len(self._stops))
        self._stops.append((pointer, item))
        return pointer

    def prepend(self, item):
        assert isinstance(item, TimeAndPlace) or item is None
        pointer = RideStopPointer(0)
        self._stops.prepend((pointer, item))
        self._alter_pointers_after(0, 1)
        return pointer

    def insert(self, position, item):
        assert isinstance(item, TimeAndPlace) or item is None
        position = max(0, min(position, len(self._stops)))
        pointer = RideStopPointer(position)
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
        self._serial_add(data, 'bike_friendly', ids)
        if self._stops:
            stops = [(stop[1].serialize(ids) if stop[1] is not None else None) for stop in self._stops]
            self._serial_add(data, 'stops', ids, val=stops)
        return data


class RideStopPointer():
    def __init__(self, i: int):
        self._i = i

    def __int__(self):
        return self._i

    def __index__(self):
        return self._i

    def __repr__(self):
        return 'p:%d' % self._i


class RideSegment():
    def __init__(self, ride: Ride, origin: RideStopPointer=None, destination: RideStopPointer=None):
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
                raise NotImplementedError('slicing a RideSegment with steps is not supported')
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
            return RideSegment(self.ride, start, stop)
        else:
            if type(key) != int:
                return self.ride[key]
            else:
                return self._stops()[key][1]

    def __iter__(self, key):
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
        return (isinstance(other, RideSegment) and self.ride == other.ride and
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


class Way(ModelBase):
    def __init__(self, origin: Location, destination: Location, distance: int=None):
        super().__init__()
        self.origin = origin
        self.destination = destination
        self.distance = None
        self.duration = None
        # todo: self.stairs = None

    @classmethod
    def load(cls, data):
        origin = Location.unserialize(data['origin'])
        destination = Location.unserialize(data['destination'])
        obj = cls(origin, destination)
        obj.distance = data.get('distance', None)
        obj.duration = data.get('duration', None)
        return obj

    def __eq__(self, other):
        return (isinstance(other, Way) and self.origin == other.origin and self.destination == other.destination)

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, 'origin', ids)
        self._serial_add(data, 'destination', ids)
        self._serial_add(data, 'distance', ids)
        self._serial_add(data, 'duration', ids)
        return data


class Trip(ModelBase):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.walk_speed = 'normal'

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
        
        
class TripRequest(ModelBase):
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
        

