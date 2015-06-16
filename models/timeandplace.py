#!/usr/bin/env python3
from .base import Updateable
from .locations import Platform
from .realtime import RealtimeTime


class TimeAndPlace(Updateable):
    def __init__(self, platform=None, arrival=None, departure=None):
        super().__init__()
        self.platform = platform
        self.arrival = arrival
        self.departure = departure
        self.passthrough = False

    @classmethod
    def _validate(cls):
        return (
            ('platform', Platform),
            ('arrival', (None, RealtimeTime)),
            ('departure', (None, RealtimeTime)),
            ('passthrough', bool),
        )

    _update_default = ('platform', 'passthrough')

    def _update(self, other, better):
        if self.arrival is None:
            self.arrival = other.arrival
        else:
            self.arrival.update(other.arrival)

        if self.departure is None:
            self.departure = other.departure
        else:
            self.departure.update(other.departure)

        self.platform.update(other.platform)

    @property
    def stop(self):
        return self.platform.stop

    def __eq__(self, other):
        if not isinstance(other, TimeAndPlace):
            return False

        if self.platform != other.platform:
            return False

        if self.arrival is None and self.arrival == other.arrival:
            return True

        if self.departure is None and self.departure == other.departure:
            return True

        return False

    def __repr__(self):
        return ('<TimeAndPlace %s %s %s>' % (self.arrival, self.departure, self.platform))
