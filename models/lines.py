#!/usr/bin/env python3
from .base import ModelBase

class LineTypes(ModelBase):
    _known = ('localtrain', 'longdistance', 'highspeed', 'urban', 'metro', 'tram',
              'citybus', 'regionalbus', 'expressbus', 'suspended', 'ship', 'dialable',
              'other', 'walk')
    _shortcuts = {
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
                if name not in self._included:
                    return False
            return True

    def __nonzero__(self):
        return bool(self._included)

    def __eq__(self, other):
        return (isinstance(other, LineTypes) and self._incluced == other._included)

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

    def _load(self, data):
        super()._load(data)
        self._serial_get(data, 'linetype')
        self._serial_get(data, 'product')
        self._serial_get(data, 'name')
        self._serial_get(data, 'shortname')
        self._serial_get(data, 'route')
        self._serial_get(data, 'first_stop')
        self._serial_get(data, 'last_stop')
        self._serial_get(data, 'network')
        self._serial_get(data, 'operator')

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, 'linetype', ids)
        self._serial_add(data, 'product', ids)
        self._serial_add(data, 'name', ids)
        self._serial_add(data, 'shortname', ids)
        self._serial_add(data, 'route', ids)
        self._serial_add(data, 'first_stop', ids)
        self._serial_add(data, 'last_stop', ids)
        self._serial_add(data, 'network', ids)
        self._serial_add(data, 'operator', ids)
        return data
