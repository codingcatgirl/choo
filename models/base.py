#!/usr/bin/env python3
from collections import Iterable
import copy


class Serializable:
    _serialize_depth = None

    def validate(self):
        for c in self.__class__.__mro__:
            if not hasattr(c, '_validate'):
                continue

            mycls = self.__class__.__name__

            for name, allowed in c._validate().items():
                if not hasattr(self, name):
                    raise AttributeError('%s.%s is missing' % (mycls, name))

                if not self._validate_item(getattr(self, name), allowed):
                    raise ValueError('%s.%s has to be %s, not %s' % (mycls, name, self._validate_or(allowed), repr(getattr(self, name))))
        return True

    def _validate_item(self, val, alloweds):
        if type(alloweds) != tuple:
            alloweds = (alloweds, )

        for allowed in alloweds:
            if allowed is None:
                if val is None:
                    return True
            elif type(allowed) is tuple:
                if not isinstance(val, Iterable):
                    return False

                for v in val:
                    if not self._validate_item(v, allowed):
                        return False
                return True
            elif isinstance(val, allowed):
                return True
        return False

    def _validate_or(self, items):
        if type(items) != tuple:
            return items.__name__
        out = []
        for item in items:
            if item is None:
                out.append('None')
            elif type(item) is tuple:
                out.append('Iterable(%s)' % self._validate_or(item))
            else:
                out.append(item.__name__)

        out = [(', ' + o) for o in out]
        if len(out) > 1:
            out[-1] = ' or ' + out[-1][2:]
        return ''.join(out)[2:]

    def _unserialize_typed(self, data, types=None):
        type_, data = data
        for t in types:
            if t._serialized_name() == type_:
                return t.unserialize(data)
        raise TypeError('Wrong datatype for unserialization')

    def serialize(self, depth=None, typed=False):
        self.validate()
        if depth is None:
            depth = self._serialize_depth

        serialized = {}
        if depth != 0:
            for c in self.__class__.__mro__:
                if not hasattr(c, '_serialize'):
                    continue
                more = c._serialize(self, (depth - 1 if depth is not None else None))
                if not isinstance(more, dict):
                    return more
                serialized.update(more)

        if typed:
            return self.__class__._serialized_name(), serialized
        else:
            return serialized

    @classmethod
    def _serialized_name(cls):
        if hasattr(cls, 'Model'):
            return cls.Model.__name__ + '.' + cls.__name__
        else:
            return cls.__name__

    def _serialize(self, depth):
        return {}

    @classmethod
    def unserialize(cls, data):
        obj = cls()
        for c in cls.__mro__:
            if hasattr(c, '_unserialize'):
                c._unserialize(obj, data)
        return obj

    def _unserialize(self, data):
        pass

    def _serial_add(self, data, name, force=False):
        val = getattr(self, name)
        if force or val is not None:
            data[name] = val

    def _serial_get(self, data, name, types=None):
        if name in data:
            if types is None:
                setattr(self, name, data[name])
            else:
                if isinstance(types, ModelBase):
                    types = (types, )


class MetaModelBase(type):
    def __init__(cls, a, b, c):
        cls.Request.Model = cls
        cls.Results.Model = cls


class ModelBase(Serializable, metaclass=MetaModelBase):
    @classmethod
    def _validate(cls):
        return {
            '_ids': dict
        }

    def __init__(self):
        self._ids = {}

    def _serialize(self, depth):
        data = {}
        data['_ids'] = self._ids
        return data

    def _unserialize(self, data):
        self._serial_get(data, '_ids')
        for name, val in tuple(self._ids.items()):
            if type(val) == list:
                self._ids[name] = tuple(val)

    def matches(self, request):
        if not isinstance(request, ModelBase.Request):
            raise TypeError('not a request')
        return request.matches(self)

    class Request(Serializable):
        def matches(self, obj):
            if not isinstance(obj, self.Model):
                raise TypeError('%s.Request can only match %s' % (self.Model.__name__, self.Model.__name__))
            obj.validate()
            return self._matches(obj)

        def _matches(obj):
            pass

    class Results(Serializable):
        def __init__(self, results=[]):
            super().__init__()
            self.results = tuple(results)

        def _serialize(self, depth):
            data = {}
            data['results'] = [((r[0].serialize(), ) + r[1:])
                               for r in self.results]
            return data

        def _unserialize(self, data):
            self.results = [((self.Model.unserialize(d[0]), ) + d[1:]) for d in data['results']]

        def filter(self, request):
            if not self.results:
                return

            if not isinstance(request, self.Model.Request):
                raise TypeError('%s.Results can be filtered with %s' % (self.Model.__name__, self.Model.__name__))

            self.results = tuple(r for r in self.results if request.matches(r))

        def filtered(self, request):
            obj = copy.copy(self)
            obj.filter(request)
            return obj

        def __iter__(self):
            for result in self.results:
                yield result

        def __getitem__(self, key):
            return self.results[key]
