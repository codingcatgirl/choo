#!/usr/bin/env python3
from .base import ModelBase
from .lines import LineTypes

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
