#!/usr/bin/env python3
from datetime import datetime, timedelta


class ModelBase():
    def __init__(self):
        self._ids = {}
        self._raws = {}

    def _load(self, data):
        self._ids = data.get('ids', {})

    def serialize(self, ids=None):
        if ids is None:
            ids = []
        myid = id(self)
        if len(ids) != len(set(ids)):
            return {}
        return self._serialize(ids+[myid])

    def _serialize(self, ids):
        data = {}
        if self._ids:
            data['ids'] = self._ids
        return data

    def _add_not_none(self, data, name):
        val = getattr(self, name)
        if val:
            data[name] = val

    def _add_not_none_obj(self, data, name, ids):
        val = getattr(self, name)
        if val:
            data[name] = val.serialize(ids)


class SearchResults():
    def __init__(self, results, subject=None, api=None, method=None):
        self.subject = subject
        self.api = api
        self.method = method
        self.results = tuple(results)

    @classmethod
    def load(cls, data):
        obj = cls(data.get('results', []))
        obj.subject = data.get('subject', None)
        obj.api = data.get('api', None)
        obj.method = data.get('method', None)
        # todo – load subject
        return obj

    def __iter__(self):
        for result in self.results:
            yield result

    def __getitem__(self, key):
        return self.results[key]

    def _serialize(self, ids):
        data = {}
        if self.subject is not None:
            data['subject'] = self.subject.serialize(ids)
        if self.api is not None:
            data['api'] = self.api
        if self.method is not None:
            data['method'] = self.method
        if self.results:
            if type(self.results[0]) == tuple:
                data['results'] = [(item[0].__class__.__name__.lower(), (item[0].serialize(ids), item[1])) for item in self.results]
            else:
                data['results'] = [(item.__class__.__name__.lower(), item.serialize(ids)) for item in self.results]
        return data


class Location(ModelBase):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        self.country = country
        self.city = city
        self.name = name
        self.coords = coords

    def _load(self, data):
        self.country = data.get('country', None)
        self.city = data.get('city', None)
        self.name = data.get('name', None)
        self.coords = data.get('coords', None)
        super()._load(data)

    @classmethod
    def load(cls, data):
        obj = cls()
        obj._load(data)
        return obj

    def _serialize(self, ids):
        data = super()._serialize(ids)
        data.update({
            'country': self.country,
            'city': self.city,
            'name': self.name,
        })
        self._add_not_none(data, 'coords')
        if self.coords:
            data['coords'] = self.coords
        return data


class Stop(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)
        self.rides = []
        self.lines = []

    @classmethod
    def load(cls, data):
        obj = cls()
        obj.rides = data.get('rides', None)
        if obj.rides:
            obj.rides = [RideSegment.load(ride) for ride in obj.rides]
        obj._load(data)
        return obj

    def __repr__(self):
        return '<%s %s, %s>' % (self.__class__.__name__, self.city, self.name)

    def _serialize(self, ids):
        data = super()._serialize(ids)
        if self.rides:
            data['rides'] = [ride.serialize(ids) for ride in self.rides]
            if data['rides'].count({}) == len(data['rides']):
                data['rides'] = []

        if self.lines:
            data['lines'] = [line.serialize(ids) for line in self.lines]
            if data['lines'].count({}) == len(data['lines']):
                data['lines'] = []
        return data


class POI(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)

    @classmethod
    def load(cls, data):
        obj = cls()
        obj._load(data)
        return obj

    def _serialize(self, ids):
        return super()._serialize(ids)


class Address(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)

    @classmethod
    def load(cls, data):
        obj = cls()
        obj._load(data)
        return obj

    def _serialize(self, ids):
        return super()._serialize(ids)


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
        time = data.get('time', None)
        delay = data.get('delay', None)
        livetime = data.get('livetime', None)
        if time:
            time = datetime.strptime(time, '%Y-%m-%d %H:%M')
        if livetime:
            livetime = datetime.strptime(livetime, '%Y-%m-%d %H:%M')
        if delay:
            delay = timedelta(minutes=delay)
        obj = cls(time, delay, livetime)
        obj._load(data)
        return obj

    def __repr__(self):
        return '<RealtimeTime %s%s>' % (str(self.time)[:-3], (' +%d' % (self.delay.total_seconds()/60)) if self.delay is not None else '')

    @property
    def islive(self):
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
        data = super()._serialize(ids)
        data['time'] = self.time.strftime('%Y-%m-%d %H:%M')
        if self.delay is not None:
            data['delay'] = int(self.delay.total_seconds()/60)
        return data


class TimeAndPlace(ModelBase):
    def __init__(self, stop: Stop, platform: str=None, arrival: RealtimeTime=None, departure: RealtimeTime=None, coords: tuple=None):
        super().__init__()
        self.stop = stop
        self.platform = platform
        self.coords = coords
        self.arrival = arrival
        self.departure = departure

    @classmethod
    def load(cls, data):
        arrival = data.get('arrival', None)
        departure = data.get('departure', None)
        coords = data.get('coords', None)
        if arrival:
            arrival = RealtimeTime.load(arrival)
        if departure:
            arrival = RealtimeTime.load(arrival)
        if coords:
            coords = tuple(coords)

        obj = cls(data['stop'], data.get('platform', None), arrival, departure, coords)
        obj._load(data)
        return obj

    def __eq__(self, other):
        return (isinstance(other, TimeAndPlace) and self.stop == other.stop and
                self.platform == other.platform and self.arrival == other.arrival and
                self.departure == other.departure)

    def __repr__(self):
        return '<TimeAndPlace %s %s %s %s>' % (repr(self.arrival), repr(self.departure), repr(self.stop), repr(self.platform))

    def _serialize(self, ids):
        data = super()._serialize(ids)
        data['stop'] = self.stop.serialize(ids)
        self._add_not_none(data, 'platform')
        if self.arrival is not None:
            data['arrival'] = self.arrival.serialize(ids)
        if self.departure is not None:
            data['departure'] = self.departure.serialize(ids)
        self._add_not_none(data, 'coords')
        return data


class LineTypes(ModelBase):
    _known = ('localtrain', 'longdistance', 'highspeed', 'urban', 'metro', 'tram',
              'citybus', 'regionalbus', 'expressbus', 'suspended', 'ship', 'dialable',
              'others', 'walk')
    _shortcuts = {
        'longdistance': ('longdistance_other', 'ice'),
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
                if name not in self:
                    return False
            return True

    def __nonzero__(self):
        return bool(self._included)

    def __eq__(self, other):
        return (isinstance(other, LineTypes) and self._invluced == other._included)

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

    @classmethod
    def load(cls, data):
        linetype = data.get('linetype', None)
        if linetype:
            linetype = LineType.load(linetype)

        obj = cls(linetype)
        obj.product = data.get('product', None)
        obj.name = data.get('name', None)
        obj.shortname = data.get('shortname', None)
        obj.route = data.get('route', None)

        obj.first_stop = data.get('first_stop', None)
        obj.last_stop = data.get('last_stop', None)
        if obj.first_stop:
            obj.first_stop = Stop.load(obj.first_stop)
        if obj.last_stop:
            obj.last_stop = Stop.load(obj.last_stop)

        obj.network = data.get('network', None)
        obj.operator = data.get('operator', None)
        obj._load(data)
        return obj

    def _serialize(self, ids):
        data = super()._serialize(ids)
        self._add_not_none_obj(data, 'linetype', ids)
        self._add_not_none(data, 'product')
        self._add_not_none(data, 'name')
        self._add_not_none(data, 'shortname')
        self._add_not_none(data, 'route')
        self._add_not_none_obj(data, 'first_stop', ids)
        self._add_not_none_obj(data, 'last_stop', ids)
        self._add_not_none(data, 'network')
        self._add_not_none(data, 'operator')
        return data


class Ride(ModelBase):
    def __init__(self, line: Line=None, number: str=None):
        super().__init__()
        self._stops = []
        self.line = line
        self.number = number
        self.bike_friendly = None

    @classmethod
    def load(cls, data):
        line = data.get('line', None)
        stops = data.get('stops', [])
        number = data.get('number', None)
        if line:
            line = Line.load(line)
        if stops:
            stops = [(TimeAndPlace.load(stop) if stop is not None else None) for stop in stops]

        obj = cls(line, number)
        obj.bike_friendly = data.get('bike_friendly', None)
        for stop in stops:
            obj.append(stop)
        obj._load(data)
        return obj

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
        data = super()._serialize(ids)
        self._add_not_none_obj(data, 'line', ids)
        self._add_not_none(data, 'number')
        self._add_not_none(data, 'bike_friendly')
        if self._stops:
            data['stops'] = [(stop[1].serialize(ids) if stop[1] is not None else None) for stop in self._stops]
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
        ride = Ride.load(data['ride'])
        origin = data.get('origin', None)
        destination = data.get('destination', None)
        me = ride[origin:destination]
        obj = cls(ride, me._pointer_origin, me._pointer_destination)
        return obj

    def _stops(self):
        return self.ride.stops[self._pointer_origin:self._pointer_destination]

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
        origin = globals()[data['origin'][0]].load(data['origin'][1])
        destination = globals()[data['destination'][0]].load(data['destination'][1])
        obj = cls(origin, destination)
        obj.distance = data.get('distance', None)
        obj.duration = data.get('duration', None)
        return obj

    def __eq__(self, other):
        return (isinstance(other, Way) and self.origin == other.origin and self.destination == other.destination)

    def _serialize(self, ids):
        data = super()._serialize(ids)
        data['origin'] = (self.origin.__class__.__name__, self.origin)
        data['destination'] = (self.destination.__class__.__name__, self.destination)
        self._add_not_none(data, 'distance')
        self._add_not_none(data, 'duration')
        return data


class Trip(ModelBase):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.walk_speed = 'normal'

    @classmethod
    def load(cls, data):
        obj = cls()
        parts = data.get('parts', [])
        obj.parts = [(RideSegment.load(part[1]) if part[0] == 'ride' else Way.load(part[1])) for part in parts]
        obj.walk_speed = data.get('walk_speed', None)
        # todo: optional properties
        return obj

    def __getattr__(self, name):
        if name == 'origin':
            return None if not self.parts else self.parts[0].origin
        elif name == 'destination':
            return None if not self.parts else self.parts[-1].destination
        elif name == 'departure':
            delta = timedelta(0)
            for part in self.parts:
                if isinstance(part, RideSegment):
                    return None if part.departure is None else part.departure - delta
                elif part.duration is None:
                    return None
                else:
                    delta += part.duration
        elif name == 'arrival':
            delta = timedelta(0)
            for part in reversed(self.parts):
                if isinstance(part, RideSegment):
                    return None if part.arrival is None else part.arrival + delta
                elif part.duration is None:
                    return None
                else:
                    delta += part.duration
        elif name == 'linetypes':
            if not self.parts:
                return None
            types = LineTypes(False)
            for part in self.parts:
                linetype = part.line.linetype
                if linetype is not None:
                    types.add(linetype)
            return types
        elif name == 'changes':
            if not self.parts:
                return None
            return max(0, len([part for part in self.parts if isinstance(part, RideSegment)])-1)
        elif name == 'bike_friendly':
            if not self.parts:
                return None
            tmp = [part.bike_friendly for part in self.parts if isinstance(part, RideSegment)]
            if False in tmp:
                return False
            if None in tmp:
                return None
            return True

    def _serialize(self, ids):
        data = super()._serialize(ids)
        data['parts'] = [('ride' if isinstance(part, RideSegment) else 'way', part.serialize(ids)) for part in self.parts]
        self._add_not_none(data, 'walk_speed')
        # todo: optional properties
        return data
