#!/usr/bin/env python3
from .base import Searchable, TripPart
from .way import Way, WayType
from .locations import Location, AbstractLocation
from .ride import Ride, RideSegment
from .line import Line, LineType, LineTypes
from .tickets import TicketList
from datetime import timedelta, datetime


class Trip(Searchable):
    def __init__(self):
        super().__init__()
        self._parts = []
        self.tickets = None

    @staticmethod
    def _validate():
        return (
            ('_parts', None),
            ('tickets', (None, TicketList))
        )

    def _validate_custom(self, name, value):
        if name == '_parts':
            for v in value:
                if not isinstance(v, TripPart):
                    return False
            return True

    def _serialize_custom(self, name, **kwargs):
        if name == '_parts':
            return 'parts', [p.serialize(typed=True, **kwargs) for p in self._parts]

    def _unserialize_custom(self, name, data):
        if name == 'parts':
            self.parts = [self._unserialize_typed(part, (RideSegment, Way)) for part in data]

    def _collect_children(self, collection, last_update=None, ids=None):
        super()._collect_children(collection, last_update, ids=ids)

        if self.tickets is not None:
            self.tickets._update_collect(collection, last_update, ids=ids)

        for part in self._parts:
            part._update_collect(collection, last_update)

    class Request(Searchable.Request):
        def __init__(self):
            super().__init__()
            self.walk_speed = 'normal'
            self.origin = None
            self.via = []
            self.destination = None
            self.departure = None
            self.arrival = None
            self.linetypes = LineTypes()
            self.max_changes = None

            self.with_bike = False
            self.wheelchair = False
            self.low_floor_only = False
            self.allow_solid_stairs = True
            self.allow_escalators = True
            self.allow_elevators = True

            self.waytype_origin = WayType('walk')
            self.waytype_via = WayType('walk')
            self.waytype_destination = WayType('walk')

            self.wayduration_origin = timedelta(minutes=10)
            self.wayduration_via = timedelta(minutes=10)
            self.wayduration_destination = timedelta(minutes=10)

        @staticmethod
        def _validate():
            return (
                # ('walk_speed', None),
                ('origin', (None, AbstractLocation, Ride, Trip)),
                # ('via', None),
                ('destination', (None, AbstractLocation, Ride, Trip)),
                ('departure', (None, datetime)),
                ('arrival', (None, datetime)),
                ('linetypes', LineTypes),
                ('max_changes', (None, int)),

                ('with_bike', bool),
                ('wheelchair', bool),
                ('low_floor_only', bool),
                ('allow_solid_stairs', bool),
                ('allow_escalators', bool),
                ('allow_elevators', bool),

                ('waytype_origin', WayType),
                ('waytype_via', WayType),
                ('waytype_destination', WayType),

                ('wayduration_origin', timedelta),
                ('wayduration_via', timedelta),
                ('wayduration_destination', timedelta)
            )

        def _matches(self, obj):
            if self.origin != obj.origin or self.destination != obj.destination:
                return False

            if not obj.wayonly:
                if self.departure is not None and self.departure < obj.departure:
                    return False

                if self.arrival is not None and self.arrival > obj.arrival:
                    return False

            for i, part in enumerate(obj):
                if isinstance(part, RideSegment):
                    if part.line.linetype not in self.linetypes:
                        return False
                else:
                    if part.waytype == WayType('walk'):
                        continue
                    if i == 0:
                        if self.waytype_origin != part.waytype:
                            return False
                    elif i + 1 == len(obj):
                        if self.waytype_destination != part.waytype:
                            return False
                    else:
                        if self.waytype_via != part.waytype:
                            return False

            return True

    class Results(Searchable.Results):
        def __init__(self, *args):
            super().__init__(*args)
            self.origin = None
            self.via = None
            self.destination = None

        @staticmethod
        def _validate():
            return (
                ('origin', Location),
                ('via', (None, Location)),
                ('destination', Location),
            )

    @property
    def origin(self):
        return self._parts[0].origin

    @property
    def destination(self):
        return self._parts[-1].destination

    @property
    def departure(self):
        delta = timedelta(0)
        for part in self._parts:
            if isinstance(part, RideSegment):
                return (part.departure - delta) if part.departure else None
            elif part.duration is None:
                return None
            else:
                delta += part.duration

    @property
    def arrival(self):
        delta = timedelta(0)
        for part in reversed(self._parts):
            if isinstance(part, RideSegment):
                return (part.arrival + delta) if part.arrival else None
            elif part.duration is None:
                return None
            else:
                delta += part.duration

    @property
    def wayonly(self):
        for part in self:
            if isinstance(part, RideSegment):
                return False
        return True

    @property
    def linetypes(self):
        types = LineTypes(())
        for part in self._parts:
            if isinstance(part, RideSegment):
                types.include(part.line.linetype)
        return types

    @property
    def changes(self):
        changes = -1
        for part in self._parts:
            if isinstance(part, RideSegment):
                changes += 1
        return max(0, changes)

    @property
    def bike_friendly(self):
        for part in self._parts:
            if not isinstance(part, RideSegment):
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

    def __len__(self):
        return len(self._parts)

    def __getitem__(self, key):
        return self._parts[key]

    def __contains__(self, obj):
        if isinstance(obj, RideSegment):
            return obj in self._parts

        if isinstance(obj, Ride):
            compare = lambda part, obj: part.ride == obj
        elif isinstance(obj, Ride.Request):
            compare = lambda part, obj: part.ride.matches(obj)
        elif isinstance(obj, Line):
            compare = lambda part, obj: part.line == obj
        elif isinstance(obj, Line.Request):
            compare = lambda part, obj: part.line.matches(obj)
        elif isinstance(obj, LineType):
            compare = lambda part, obj: part.line.linetype == obj
        elif isinstance(obj, LineTypes):
            compare = lambda part, obj: part.line.linetype in obj
        else:
            # todo: here be more, Way, Stop, Platform, …
            raise NotImplementedError()

        for part in self.parts:
            if isinstance(part, RideSegment) and compare(part, obj):
                return True
        return False

    def __repr__(self):
        return '<Trip %s %s - %s %s>' % (repr(self.origin), str(self.departure), repr(self.origin), str(self.arrival))

    def __eq__(self, other):
        if not isinstance(other, Trip):
            return False

        for i, part in enumerate(self):
            if part != other[i]:
                return False
        return True

    def __iter__(self):
        yield from self._parts
