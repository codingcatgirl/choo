#!/usr/bin/env python3
from datetime import datetime, timedelta


class ModelBase():
    def __init__(self):
        self._ids = {}
        self._raws = {}


class SearchResults():
    def __init__(self, results, subject=None, api=None, method=None):
        self.subject = subject
        self.api = api
        self.method = method
        self.results = tuple(results)

    def __iter__(self):
        return self.results

    def __getitem__(self, key):
        return self.results[key]


class Location(ModelBase):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        self.country = country
        self.city = city
        self.name = name
        self.coords = coords


class Stop(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)
        self.rides = []

    def __repr__(self):
        return '<%s %s, %s>' % (self.__class__.__name__, self.city, self.name)


class POI(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)


class Address(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)


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


class TimeAndPlace(ModelBase):
    def __init__(self, stop: Stop, platform: str=None, arrival: RealtimeTime=None, departure: RealtimeTime=None, coords: tuple=None):
        super().__init__()
        self.stop = stop
        self.platform = platform
        self.coords = coords
        self.arrival = arrival
        self.departure = departure

    def __eq__(self, other):
        return (isinstance(other, TimeAndPlace) and self.stop == other.stop and
                self.platform == other.platform and self.arrival == other.arrival and
                self.departure == other.departure)

    def __repr__(self):
        return '<TimeAndPlace %s %s %s %s>' % (repr(self.arrival), repr(self.departure), repr(self.stop), repr(self.platform))


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


class LineType(ModelBase):
    def __init__(self, name: str):
        super().__init__()
        if name in LineTypes._known:
            self.name = name
        else:
            raise AttributeError('unsupported linetype')

    def __eq__(self, name: str):
        if self.name == name or (name in LineTypes._shortcuts and self.name in LineTypes._shortcuts[name]):
            return True
        elif name in LineTypes._known:
            return False
        else:
            raise AttributeError('unsupported linetype')


class Line(ModelBase):
    def __init__(self, linetype: LineType=None):
        super().__init__()
        self.linetype = linetype
        self.product = None
        self.name = None
        self.shortname = None
        self.route = None

        self.network = None
        self.operator = None


class Ride(ModelBase):
    def __init__(self, line: Line=None, number: str=None):
        super().__init__()
        self._stops = []
        self.line = line
        self.number = number
        self.bike_friendly = None

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


class Way(ModelBase):
    def __init__(self, origin: Location, destination: Location, distance: int=None):
        super().__init__()
        self.origin = origin
        self.destination = destination
        self.distance = None
        self.duration = None
        # todo: self.stairs = None

    def __eq__(self, other):
        return (isinstance(other, Way) and self.origin == other.origin and self.destination == other.destination)


class Trip(ModelBase):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.walk_speed = 'normal'

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
