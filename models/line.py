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


class LineType(Serializable):
    _known = (
        '', 'train', 'train.local', 'train.longdistance', 'train.longdistance.highspeed',
        'urban', 'metro', 'tram',
        'bus', 'bus.regional', 'bus.city', 'bus.express',
        'suspended', 'ship', 'dialable', 'other'
    )
    _created = {}

    def __new__(cls, value=''):
        if isinstance(value, cls):
            return value
        elif value not in cls._known:
            raise AttributeError('invalid linetype: %s' % repr(value))
        if value in cls._created:
            return cls._created[value]
        else:
            self = super().__new__(cls)
            self._value = value
            cls._created[value] = self
            return self

    def _serialize(self, depth):
        return self._value

    @classmethod
    def unserialize(cls, data):
        return cls(data)

    def __repr__(self):
        return 'LineType(%s)' % repr(self._value)

    def __str__(self):
        return self._value

    def __contains__(self, other):
        if type(other) == 'str':
            other = LineType(other)
        self._value.startswith(other._value)


class LineTypes(Serializable):
    def __init__(self, include=(''), exclude=()):
        super().__init__()
        self._included = set([LineType(s) for s in include])
        self._excluded = set([LineType(s) for s in exclude])

    def _serialize(self, depth):
        data = {}
        data['include'] = [str(s) for s in self._include]
        if self._exclude:
            data['exclude'] = [str(s) for s in self._exclude]

    def _unserialize(self, data):
        if 'include' in data:
            self._included = set([LineType(s) for s in data['include']])
        if 'exclude' in data:
            self._excluded = set([LineType(s) for s in data['exclude']])

    def include(self, *args):
        args = [LineType(a) for a in args]
        for include in args[:]:
            args = [a for a in args if a not in include]

        for include in args:
            self._included = [i for i in self._included if i not in include]
            self._exclude = [e for e in self._excluded if e in include]

        self._included = set(self._included + args)
        self._excluded = set([e for e in self._excluded if [i for i in self._included if e in i]])

    def exclude(self, *args):
        args = [LineType(a) for a in args]
        for exclude in args[:]:
            args = [a for a in args if a not in exclude]

        for exclude in args:
            self._included = [i for i in self._included if i not in exclude]
            self._exclude = [e for e in self._excluded if e in exclude]

        self._included = set(self._included)
        self._excluded = set(self._excluded + args)
        self._excluded = set([e for e in self._excluded if [i for i in self._included if e in i]])

    def __contains__(self, linetype):
        linetype = LineType(linetype)
        for exclude in self._excluded:
            if linetype in exclude:
                return False

        for include in self._included:
            if linetype in include:
                return True

        return False
