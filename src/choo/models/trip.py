from datetime import timedelta

from ..types import LineTypes, LiveTime, WayEvent, WayType
from .base import Field, Model
from .locations import GeoPoint, Location
from .tickets import TicketList

RideSegment = 1


class Trip(Model):
    origin = Field(Location)
    # via = Field(Iterable[Location])
    destination = Field(Location)
    parts = Field(list)
    tickets = Field(TicketList)
    departure = Field(LiveTime)
    arrival = Field(LiveTime)
    linetypes = Field(LineTypes)

    with_bike = Field(bool)
    wheelchair = Field(bool)
    low_floor_only = Field(bool)
    no_solid_stairs = Field(bool)
    no_escalators = Field(bool)
    no_elevators = Field(bool)

    waytype_origin = Field(WayType)
    waytype_via = Field(WayType)
    waytype_destination = Field(WayType)

    wayduration_origin = Field(timedelta)
    wayduration_via = Field(timedelta)
    wayduration_destination = Field(timedelta)

    @property
    def origin(self):
        return self._parts[0].origin

    @property
    def destination(self):
        return self._parts[-1].destination

    @property
    def departure(self):
        # delta = timedelta(0)
        for part in self._parts:
            # if isinstance(part, RideSegment):
            #     return (part.departure - delta) if part.departure else None
            # elif part.duration is None:
            #     return None
            # else:
            #     delta += part.duration
            pass

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

    def __len__(self):
        return len(self._parts)

    def __getitem__(self, key):
        return self._parts[key]

    def __contains__(self, obj):
        if isinstance(obj, RideSegment):
            return obj in self._parts

        """
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
        """

    def __repr__(self):
        return '<Trip %s %s - %s %s>' % (repr(self.origin), str(self.departure), repr(self.origin), str(self.arrival))

    def __eq__(self, other):
        if not isinstance(other, Trip):
            return False

        for i, part in enumerate(self):
            compared = part == other[i]
            if compared is not True:
                return compared
        return True

    def __iter__(self):
        yield from self._parts


class Way(Model):
    waytype = Field(WayType)
    origin = Field(GeoPoint)
    destination = Field(GeoPoint)
    distance = Field(float)
    duration = Field(timedelta)
    events = Field(WayEvent)
    # path = Field(Iterable[Coordinates])

    def __eq__(self, other):
        if not isinstance(other, Way):
            return False

        if self.waytype != other.waytype:
            return False

        compared = self.origin == other.origin
        if compared is not True:
            return compared

        compared = self.destination == other.destination
        if compared is not True:
            return compared

        return True

    def __repr__(self):
        distance = ''
        if self.distance:
            distance = ' %dm' % self.distance
        return '<Way %s %s %s %s %s>' % (
            str(self.waytype), self.duration,
            distance, repr(self.origin), repr(self.destination))
