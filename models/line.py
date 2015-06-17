#!/usr/bin/env python3
from .base import Collectable, Serializable


class Line(Collectable):
    @classmethod
    def _validate(cls):
        from .locations import Stop
        return (
            ('linetype', (None, LineType)),
            ('product', (None, str)),
            ('name', (None, str)),
            ('shortname', (None, str)),
            ('route', (None, str)),
            ('first_stop', (None, Stop)),
            ('last_stop', (None, Stop)),
            ('network', (None, str)),
            ('operator', (None, str)),
        )

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

    _update_default = ('product', 'name', 'shortname', 'route', 'network', 'operator')

    def _update(self, other, better):
        if other.linetype in self.linetype:
            self.linetype = other.linetype

    def __eq__(self, other):
        if not isinstance(other, Line):
            return False

        if self.linetype not in other.linetype and other.linetype not in self.linetype:
            return False

        byid = self._equal_by_id(other)
        if byid is not None:
            return byid

        if self.route == other.route and self.name == other.name:
            return True

        if (self.shortname is not None and other.shortname is not None and
            len([s for s in self.shortname if s.isdigit()]) and
            self.operator is not None and self.operator == other.operator and
            self.network is not None and self.network == other.network):
            return True

        return False

    def __repr__(self):
        return '<Line %s %s>' % (str(self.linetype), repr(self.name))

    class Request(Collectable.Request):
        pass

    class Results(Collectable.Results):
        pass


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

    def _serialize(self):
        return self._value

    @classmethod
    def unserialize(cls, data):
        return cls(data)

    def __repr__(self):
        return 'LineType(%s)' % repr(self._value)

    def __str__(self):
        return self._value

    def __contains__(self, other):
        if type(other) == str:
            other = LineType(other)
        return other._value.startswith(self._value)


class LineTypes(Serializable):
    def __init__(self, include=('', ), exclude=()):
        super().__init__()
        self._included = set([LineType(s) for s in include])
        self._excluded = set([LineType(s) for s in exclude])

    @classmethod
    def _validate(cls):
        return (
            ('_included', None),
            ('_excluded', None),
        )

    def _validate_custom(self, name, value):
        if name in ('_included', '_excluded'):
            if not isinstance(value, set):
                return False
            for v in value:
                if not isinstance(v, LineType):
                    return False
            return True

    def _serialize_custom(self, name):
        if name == '_included':
            return 'included', [str(s) for s in self._included]
        elif name == '_excluded':
            return 'excluded', [str(s) for s in self._excluded]

    def _unserialize_custom(self, name, data):
        if name == 'included':
            self._included = set([LineType(s) for s in data])
        elif name == 'excluded':
            self._excluded = set([LineType(s) for s in data])

    def _unserialize(self, data):
        if 'include' in data:
            self._included = set([LineType(s) for s in data['include']])
        if 'exclude' in data:
            self._excluded = set([LineType(s) for s in data['exclude']])

    def __repr__(self):
        args = []
        if tuple(self._included) != ('', ):
            args.append('%s' % repr(tuple(str(s) for s in self._included)))
        if self._excluded:
            args.append(('exclude=' if not args else '') + '%s' % repr(tuple(str(s) for s in self._excluded)))
        return 'LineTypes(%s)' % ', '.join(args)

    def include(self, *args):
        args = [LineType(a) for a in args]
        for include in args[:]:
            args = [a for a in args if a not in include or a is include]
        args = list(set(args))

        if not args:
            return

        for include in args:
            self._included = [i for i in self._included if i not in include]
            self._exclude = [e for e in self._excluded if e in include]

        self._included = set(self._included + args)
        self._excluded = set([e for e in self._excluded if [i for i in self._included if e in i]])

    def exclude(self, *args):
        args = [LineType(a) for a in args]
        for exclude in args[:]:
            args = [a for a in args if a not in exclude or a is exclude]
        args = list(set(args))

        if not args:
            return

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
