#!/usr/bin/env python3
from .base import ModelBase
from .way import Way
from .locations import Coordinates, Location, Stop, POI, Address
from .ride import RideSegment
from .line import LineTypes
from .tickets import TicketList
from datetime import timedelta


class Trip(ModelBase):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.walk_speed = 'normal'
        self.tickets = None

    @classmethod
    def _validate(cls):
        return {
            'parts': ((RideSegment, Way), ),
            'tickets': (None, TicketList)
        }

    def _serialize(self, depth):
        data = {}
        data['parts'] = [p.serialize(depth, True) for p in self.parts]
        self._serial_get(data, 'walk_speed')
        if self.tickets:
            data['tickets'] = self.tickets.serialize()
        return data

    def _unserialize(self, data):
        self.parts = [self._unserialize_typed(part, (RideSegment, Way))
                      for part in data['parts']]
        self._serial_add(data, 'walk_speed')
        if 'tickets' in data:
            self.tickets = TicketList.unserialize(data['tickets'])

    class Results(ModelBase.Results):
        def __init__(self, *args):
            super().__init__(*args)
            self.origin = None
            self.via = None
            self.destination = None

        @classmethod
        def _validate(cls):
            return {
                'origin': Location,
                'via': (None, Location),
                'destination': Location
            }

        def _load(self, data):
            super()._load(data)
            types = (Location, Stop, POI, Address, Coordinates)
            self.origin = self._unserialize_typed(data['origin'], types)
            self.destination = self._unserialize_typed(data['destination'], types)

        def _serialize(self, depth):
            data = {}
            data['origin'] = self.origin.serialize(depth, True)
            data['destination'] = self.destination.serialize(depth, True)
            return data

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
            if isinstance(part, RideSegment):
                return (part.departure - delta) if part.departure else None
            elif part.duration is None:
                return None
            else:
                delta += part.duration

    @property
    def arrival(self):
        delta = timedelta(0)
        for part in reversed(self.parts):
            if isinstance(part, RideSegment):
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
            if isinstance(part, RideSegment):
                changes += 1
        return max(0, changes)

    @property
    def bike_friendly(self):
        for part in self.parts:
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
