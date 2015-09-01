#!/usr/bin/env python3
from collections import OrderedDict
from . import fields
import copy


class MetaSerializable(type):
    def __new__(mcs, name, bases, attrs):
        class_ = super(MetaSerializable, mcs).__new__(mcs, name, bases, attrs)
        class_._fields = class_._fields.copy()
        class_._fields.update(OrderedDict(sorted(
            [(n, v) for n, v in attrs.items() if isinstance(v, fields.Field)],
            key=lambda v: v[1].i)
        ))
        return class_

    def __init__(cls, name, bases, attrs):
        if name not in ('Request', 'Results', 'Result'):
            fields.Model.add_model(cls)


class Serializable(metaclass=MetaSerializable):
    _fields = OrderedDict()

    def __init__(self, *args, **kwargs):
        self.serialize = self._serialize_instance
        for name, field in self.__class__._fields.items():
            if name in kwargs and (field.none or kwargs[name] is not None):
                setattr(self, name, kwargs[name])
            elif field.none:
                setattr(self, name, None)
            else:
                setattr(self, name, field.type())

    def validate(self):
        for name, field in self._fields.items():
            if not field.validate(getattr(self, name)):
                return False
        return True

    @classmethod
    def serialize(cls, obj):
        assert isinstance(obj, cls)
        if obj.__class__ is cls:
            return obj.serialize()
        else:
            return [obj.__class__._serialized_name(), obj.serialize()]

    def _serialize_instance(self):
        self.validate()

        data = {(name[1:] if name.startswith('_') else name): field.serialize(getattr(self, name))
                for name, field in self._fields.items()}
        return {name: field for name, field in data.items() if field is not None}

    @classmethod
    def unserialize(cls, data):
        if isinstance(data, list) and len(data) == 2:
            model_, data = data
            assert model_ in fields.Model._models
            cls_ = fields.Model._models[model_]
            assert issubclass(cls_, cls)
            return cls_.unserialize(data)
        kwargs = {}
        for name, field in cls._fields.items():
            n = name[1:] if name.startswith('_') else name
            if n in data:
                kwargs[name] = field.unserialize(data[n])

        if issubclass(cls, Searchable.Results):
            return cls(scored=True, **kwargs)
        else:
            return cls(**kwargs)

    @classmethod
    def _serialized_name(cls):
        if hasattr(cls, 'Model'):
            return cls.Model.__name__ + '.' + cls.__name__
        else:
            return cls.__name__

    def __ne__(self, other):
        return not (self == other)

    def apply_recursive(self, **kwargs):
        # print(self.__class__)
        for name, field in self.__class__._fields.items():
            value = getattr(self, name)
            field.apply_recursive(value, **kwargs)


class MetaSearchable(MetaSerializable):
    def __new__(mcs, name, bases, attrs):
        if 'Request' not in attrs:
            attrs['Request'] = type('Request', (bases[0].Request,), {'__module__': attrs['__init__'].__module__})
        if 'Results' not in attrs:
            attrs['Results'] = type('Results', (bases[0].Results,), {'__module__': attrs['__init__'].__module__})

        return super(MetaSearchable, mcs).__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        cls.Request.Model = cls
        cls.Results.Model = cls
        fields.Model.add_model(cls.Request)
        fields.Model.add_model(cls.Results)
        if name != 'Ride':
            cls.Results._fields['results'] = fields.List(fields.Tuple(fields.Model(cls), fields.Field(int)))
        MetaSerializable.__init__(cls, name, bases, attrs)


class MetaSearchableInner(MetaSerializable):
    def __repr__(cls):
        return repr(cls.Model)[:-2] + '.' + cls.__name__ + "'>"


class Searchable(Serializable, metaclass=MetaSearchable):
    def matches(self, request):
        if not isinstance(request, Searchable.Request):
            raise TypeError('not a request')
        return request.matches(self)

    class Request(Serializable, metaclass=MetaSearchableInner):
        limit = fields.Field(int)

        def __init__(self):
            super().__init__()
            self.limit = None

        def matches(self, obj):
            if not isinstance(obj, self.Model):
                raise TypeError('%s.Request can only match %s' % (self.Model.__name__, self.Model.__name__))
            obj.validate()
            return self._matches(obj)

        def _matches(self, obj):
            pass

    class Results(Serializable, metaclass=MetaSearchableInner):
        def __init__(self, results=[], scored=False, **kwargs):
            results = list(results) if scored else [(r, None) for r in results]
            super().__init__(results=results, **kwargs)

        def filter(self, request):
            if not self.results:
                return

            if not isinstance(request, self.Model.Request):
                raise TypeError('%s.Results can be filtered with %s' % (self.Model.__name__, self.Model.__name__))

            self.results = [r for r in self.results if request.matches(r)]

        def filtered(self, request):
            obj = copy.copy(self)
            obj.filter(request)
            return obj

        def __iter__(self):
            yield from (r[0] for r in self.results)

        def __len__(self):
            return len(self.results)

        def scored(self):
            yield from self.results

        def append(self, obj, score=None):
            self.results.append((obj, score))

        def _update(self, obj, better):
            for o in obj:
                for myo in self:
                    if o == myo:
                        myo.update(o)
                        break
                else:
                    self.append(myo)

        def __getitem__(self, key):
            return self.results[key]


class NetworkID(Serializable):
    pass


class Collectable(Searchable):
    id = fields.Any()
    source = fields.Field(str, none=False)
    network = fields.Field(str)
    time = fields.DateTime()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def apply_recursive(self, **kwargs):
        # print(self)
        if 'time' in kwargs:
            self.time = kwargs['time']

        if 'source' in kwargs:
            self.source = kwargs['source']

        super().apply_recursive(**kwargs)

    def update(self, other):
        # todo
        """
        better = (other.last_update and self.last_update and
                  other.last_update > self.last_update and
                  (not other.low_quality or self.low_quality)) or (not other.low_quality and self.low_quality)

        if not self.last_update or better:
            self.last_update = other.last_update
            self.low_quality = other.low_quality

        for c in self.__class__.__mro__:
            if hasattr(c, '_update_default'):
                for name in c._update_default:
                    if getattr(self, name) is None or (better and getattr(other, name) is not None):
                        setattr(self, name, getattr(other, name))

            if hasattr(c, '_update'):
                c._update(self, other, better)

        for name, value in other._ids.items():
            if name in self._ids and type(value) == tuple and None in value:
                continue
            self._ids[name] = value
        """
        pass


class TripPart(Serializable):
    pass
