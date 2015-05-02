#!/usr/bin/env python3
from .base import ModelBase, Serializable


class Line(ModelBase):
    @classmethod
    def _validate(cls):
        from .locations import Stop
        return {
            'linetype': (None, LineType),
            'product': (None, str),
            'name': (None, str),
            'shortname': (None, str),
            'route': (None, str),
            'first_stop': (None, Stop),
            'last_stop': (None, Stop),
            'network': (None, str),
            'operator': (None, str)
        }

    def __init__(self, linetype=None):
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

    def _serialize(self, depth):
        data = {}
        self._serial_add(data, 'product')
        self._serial_add(data, 'name')
        self._serial_add(data, 'shortname')
        self._serial_add(data, 'route')
        self._serial_add(data, 'network')
        self._serial_add(data, 'operator')
        if self.linetype:
            data['linetype'] = self.linetype.serialize()
        if self.first_stop:
            data['first_stop'] = self.first_stop.serialize(depth)
        if self.last_stop:
            data['last_stop'] = self.last_stop.serialize(depth)
        return data

    def _unserialize(self, data):
        from .locations import Stop
        self._serial_get(data, 'product')
        self._serial_get(data, 'name')
        self._serial_get(data, 'shortname')
        self._serial_get(data, 'route')
        self._serial_get(data, 'network')
        self._serial_get(data, 'operator')
        if 'linetype' in data:
            self.linetype = LineType.unserialize(data['linetype'])
        if 'first_stop' in data:
            self.first_stop = Stop.unserialize(data['first_stop'])
        if 'last_stop' in data:
            self.last_stop = Stop.unserialize(data['last_stop'])


class LineTypes(Serializable):
    _known = ('localtrain', 'longdistance', 'highspeed', 'urban', 'metro',
              'tram', 'citybus', 'regionalbus', 'expressbus', 'suspended',
              'ship', 'dialable', 'other', 'walk')
    _shortcuts = {
        'bus': ('citybus', 'regionalbus', 'expressbus', 'dialbus'),
        'dial': ('dialbus', 'dialtaxi')
    }

    def __init__(self, all_types: bool=True):
        super().__init__()
        self._included = set(self._known) if all_types else set()

    def _serialize(self, depth):
        return self._included

    def _unserialize(self, data):
        self._included = data

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
                for child in self._shortcuts[name]:
                    if child not in self._included:
                        return False
                return True
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
        assert isinstance(other, LineTypes)
        return self._incluced == other._included


class LineType(Serializable):
    def __init__(self, name=None):
        super().__init__()
        if name is None or name in LineTypes._known:
            self.name = name
        else:
            raise AttributeError('unsupported linetype')

    def _serialize(self, depth):
        return self.name

    def _unserialize(self, data):
        self.name = data

    def __str__(self):
        return self.name

    def __eq__(self, other):
        assert isinstance(other, LineType) or type(other) == str
        name = str(other)
        if self.name == name or (name in LineTypes._shortcuts and
                                 self.name in LineTypes._shortcuts[name]):
            return True
        elif name in LineTypes._known:
            return False
        else:
            raise AttributeError('unsupported linetype')
