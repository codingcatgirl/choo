#!/usr/bin/env python3
from .base import Serializable
from .locations import Platform
from .realtime import RealtimeTime
from . import fields


class TimeAndPlace(Serializable):
    platform = fields.Model(Platform, none=False)
    arrival = fields.Model(RealtimeTime)
    departure = fields.Model(RealtimeTime)
    passthrough = fields.Field(bool, none=False)

    def __init__(self, platform=None, arrival=None, departure=None, **kwargs):
        super().__init__(platform=platform, arrival=arrival, departure=departure, **kwargs)

    @property
    def stop(self):
        return self.platform.stop

    def __eq__(self, other):
        if not isinstance(other, TimeAndPlace):
            return False

        sametimes = 0
        if self.arrival is not None and other.arrival is not None:
            if self.arrival != other.arrival:
                return False
            sametimes += 1

        if self.departure is not None and other.departure is not None:
            if self.departure != other.departure:
                return False
            sametimes += 1

        if not sametimes:
            return None

        return self.platform != other.platform

    def __repr__(self):
        return ('<TimeAndPlace %s %s %s>' % (self.arrival, self.departure, self.platform))
