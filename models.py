#!/usr/bin/env python3
from datetime import datetime, timedelta


class Location():
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        self.country = country
        self.city = city
        self.name = name
        self.coords = coords


class Stop(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        Location.__init__(self, country, city, name, coords)
        self.rides = []


class POI(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        Location.__init__(self, country, city, name, coords)


class Address(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        Location.__init__(self, country, city, name, coords)


class RealtimeTime():
    def __init__(self, time: datetime, delay: timedelta=None, livetime: datetime=None):
        if livetime is not None:
            if delay is not None:
                assert livetime-time == delay
            else:
                delay = livetime-time

        self.time = time
        self.delay = delay

    @property
    def islive(self):
        return self.delay is not None

    @property
    def livetime(self):
        return self.time+self.delay


class TimeAndPlace():
    def __init__(self, stop: Stop, platform: str=None, arrival: RealtimeTime=None, departure: RealtimeTime=None):
        self.stop = stop
        self.platform = platform
        self.arrival = arrival
        self.departure = departure

    def __eq__(self, other):
        return (isinstance(other, TimeAndPlace) and self.stop == other.stop and
                self.platform == other.platform and self.arrival == other.arrival and
                self.departure == other.departure)


class LineTypes():
    _known = ('localtrain', 'longdistance_other', 'ice', 'urban', 'metro', 'tram',
              'citybus', 'regionalbus', 'expressbus', 'suspended', 'ship', 'dialbus',
              'dialtaxi', 'others')
    _shortcuts = {
        'longdistance': ('longdistance_other', 'ice'),
        'bus': ('citybus', 'regionalbus', 'expressbus', 'dialbus'),
        'dial': ('dialbus', 'dialtaxi')
    }

    def __init__(self, none: bool=False):
        self._included = set() if none else set(self._known)

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


class LineType():
    def __init__(self, name: str):
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


class Line():
    def __init__(self, linetype: LineType):
        self.linetype = linetype


class Ride():
    def __init__(self, line: Line=None):
        self._stops = [(RideStopPointer(0), None)]
        self.line = line

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

    def _alter_pointers_after(pos: int, diff: int):
        for stop in self._stops[pos+1:]:
            stop[0]._i += diff

    def append(self, item):
        assert isinstance(item, TimeAndPlace) or item is None
        self._stops.append((RideStopPointer(len(self._stops)), item))

    def prepend(self, item):
        assert isinstance(item, TimeAndPlace) or item is None
        self._stops.prepend((RideStopPointer(0), item))
        self._alter_pointers_after(0, 1)

    def insert(self, position, item):
        assert isinstance(item, TimeAndPlace) or item is None
        position = max(0, min(position, len(self._stops)))
        self._stops.insert(position, (RideStopPointer(len(self._stops)), item))
        self._alter_pointers_after(position, 1)

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


class RideSegment():
    def __init__(self, ride: Ride, origin: RideStopPointer=None, destination: RideStopPointer=None):
        self.ride = ride
        self.origin = origin
        self.destination = destination

    def _stops(self):
        return self.ride.stops[self.origin:self.destination]

    def is_complete(self):
        return None not in self._stops()

    def __len__(self):
        return len(self._stops)

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step is not None:
                raise NotImplementedError('slicing a RideSegment with steps is not supported')
            if self.origin is not None:
                start = key.start if type(key.start) != int else RideStopPointer(int(self.origin)+key.start)
                stop = key.stop if type(key.stop) != int else RideStopPointer(int(self.origin)+key.stop)
            else:
                start, stop = key.start, key.stop
            return RideSegment(self.ride, start, stop)
        else:
            if type(key) != int:
                return self.ride[key]
            else:
                return self._stops[key][1]

    def __iter__(self, key):
        for stop in self._stops():
            yield stop[1]

    def items(self, key):
        for stop in self._stops():
            yield stop

    def __eq__(self, other):
        return (isinstance(other, RideSegment) and self.ride == other.ride and
                self.origin == other.origin and self.destination == other.destination)


class Way():
    def __init__(self, origin: Location, destination: Location, distance: int=None):
        self.origin = origin
        self.destination = destination
        self.distance = None

    def __eq__(self, other):
        return (isinstance(other, Way) and self.origin == other.origin and self.destination == other.destination)


class Trip():
    def __init__(self):
        self.parts = []
