#!/usr/bin/env python3
from .base import Serializable
from datetime import datetime, timedelta
import bisect


class DelayHistory(Serializable):
    def __init__(self, time=None, delay=None):
        super().__init__()
        self._times = []
        self._delays = []

        self._future_times = []
        self._future_delays = []

        if time is not None and delay is not None:
            self._times.append(time)
            self._delays.append(delay)

    def __nonzero__(self):
        return len(self._times) > 0

    def __len__(self):
        return len(self._times)

    def __getitem__(self, key):
        times = self._times + self._future_times
        delays = self._delays + self._future_delays
        pos = bisect.bisect(times, key)

        if pos == 0:
            return None

        btime = times[pos - 1]
        bdelay = delays[pos - 1]
        if pos == len(times):
            return bdelay

        return bdelay + (delays[pos] - bdelay) * ((key - btime) / (times[pos] - btime))

    def __setitem__(self, key, value):
        pos = bisect.bisect(self._times, key)
        self._times.insert(pos, key)
        self._delays.insert(pos, value)

    def __delitem__(self, key):
        pos = self._times.index(key)
        del self._times[pos]
        del self._delays[pos]

    def __iter__(self, key):
        yield from self._times

    def __contains__(self, key):
        return key in self._times

    def apply(self, time):
        return RealtimeTime(time, self[time])

    @property
    def last_time(self):
        return self._times[-1]

    @property
    def last_delay(self):
        return self._delays[-1]

    @property
    def last_state(self):
        return self._times[-1], self._delays[-1]

    def items(self):
        yield from zip(self._times, self._delays)

    def future_items(self):
        yield from zip(self._future_times, self._future_delays)

    @property
    def has_future(self):
        return len(self._future_times) > 0

    def add_future(self, key, value):
        self._future_times.append(key)
        self._future_delays.append(value)

    def clear_future(self):
        self._future_times = []
        self._future_delays = []


class RealtimeTime(Serializable):
    def __init__(self, time=None, delay=None, livetime=None):
        super().__init__()
        if time is not None and livetime is not None:
            if delay is not None:
                assert livetime - time == delay
            else:
                delay = livetime - time

        self.time = time
        self.delay = delay

    @classmethod
    def _validate(cls):
        return {
            'time': datetime,
            'delay': (None, timedelta)
        }

    def _serialize(self):
        return [self.time.strftime('%Y-%m-%d %H:%M:%S'),
                int(self.delay.total_seconds()) if self.delay is not None else None]

    def _unserialize(self, data):
        self.time = datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S')
        if data[1] is not None:
            self.delay = timedelta(seconds=data[1])

    def __repr__(self):
        return '<RealtimeTime %s>' % (str(self))

    def __str__(self):
        out = self.time.strftime('%Y-%m-%d %H:%M')
        if self.delay is not None:
            out += ' %+d' % (self.delay.total_seconds() / 60)
        return out

    @property
    def is_live(self):
        return self.delay is not None

    @property
    def livetime(self):
        if self.delay is not None:
            return self.time + self.delay
        else:
            return self.time

    def __add__(self, other):
        assert isinstance(other, timedelta)
        return RealtimeTime(self.time + other, self.delay)

    def __sub__(self, other):
        assert isinstance(other, timedelta)
        return RealtimeTime(self.time - other, self.delay)

    def __eq__(self, other):
        assert isinstance(other, RealtimeTime) or isinstance(other, datetime)
        if isinstance(other, datetime):
            return self.livetime == other
        else:
            return self.livetime == other.livetime

    def __lt__(self, other):
        assert isinstance(other, RealtimeTime) or isinstance(other, datetime)
        if isinstance(other, datetime):
            return self.livetime < other
        else:
            return self.livetime < other.livetime

    def __gt__(self, other):
        assert isinstance(other, RealtimeTime) or isinstance(other, datetime)
        if isinstance(other, datetime):
            return self.livetime < other
        else:
            return self.livetime < other.livetime
