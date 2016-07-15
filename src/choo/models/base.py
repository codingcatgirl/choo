from abc import ABCMeta
from collections import OrderedDict
from datetime import datetime

from ..apis import API
from ..apis.parsers import JSONParser, Parser, XMLParser, parser_property
from ..exceptions import ObjectNotFound
from ..types import FrozenIDs, IDs, Serializable


class Field:
    """
    A field on a choo model.
    Each field has a type and validates it when a value is set.
    """
    _i = 0

    def __init__(self, type_, reverse=None):
        self.type = type_
        self.i = Field._i
        self.reverse = reverse
        Field._i += 1

    def set_name_and_model(self, name, model):
        self.name = name
        self.model = model

        if self.reverse is not None:
            if not issubclass(self.type, Model):
                raise TypeError('reverse is not None but %s is not a Model' % repr(model))
            reverse_field = getattr(self.type, self.reverse, None)
            if not isinstance(reverse_field, ReverseField):
                raise TypeError('ReverseField %s missing on %s' % (repr(self.reverse), repr(self.type)))
        return self

    def validate(self, value):
        return value is None or isinstance(value, self.type)

    def validate_raise(self, value):
        if not self.validate(value):
            raise TypeError('Invalid type for attribute %s.' % self.name)

    def serialize(self, value, _collector=None, **kwargs):
        if isinstance(value, Serializable):
            if _collector is not None and isinstance(value, Model):
                return _collector.get(value, **kwargs)
            return value.serialize(**kwargs)
        elif isinstance(value, datetime):
            return value.isoformat()
        else:
            return value

    def unserialize(self, value):
        if issubclass(self.type, Serializable):
            return self.type.unserialize(value)
        elif issubclass(self.type, datetime):
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        else:
            return value

    def get_proxy_fields(self):
        if not issubclass(self.type, Model):
            return OrderedDict()
        return OrderedDict(((self.name+'__'+name, ProxyField(self, name)) for name in self.type._fields.keys()))

    def proxy_set(self, obj, name, value):
        subobj = getattr(obj, self.name)
        if subobj is None:
            subobj = self.type()
            setattr(obj, self.name, subobj)

        setattr(subobj, name, value)

    def proxy_get(self, obj, name):
        subobj = getattr(obj, self.name)
        return None if subobj is None else getattr(subobj, name)

    def getdefault(self, value=None):
        self.validate_raise(value)
        if self.type is IDs:
            return value or IDs()
        return value

    def get_immutable(self, value, default_source, allow_parser=False):
        value = self.getdefault(value)
        if value is None:
            return value
        if issubclass(self.type, Model):
            if isinstance(value, Parser):
                if not allow_parser:
                    value = value.sourced()
            elif not isinstance(value, tuple):
                value = value._sourced(default_source)
        elif self.type is IDs and not isinstance(value, FrozenIDs):
            value = FrozenIDs(value)
        return value

    def get_mutable(self, value):
        value = self.getdefault(value)
        if issubclass(self.type, Model):
            if isinstance(value, (Parser, tuple)):
                value = value.mutable()
        elif self.type is IDs and isinstance(value, FrozenIDs):
            value = IDs(value)
        return value

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return obj._data.get(self.name)

    def __set__(self, obj, value):
        obj._data[self.name] = self.get_mutable(value)


class ProxyField:
    """
    A proxy field on a choo model (e.g. Stop.city__name)
    """
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return self.parent.proxy_get(obj, self.name)

    def __set__(self, obj, value):
        return self.parent.proxy_set(obj, self.name, value)


class ReverseField(Field):
    def __init__(self):
        super().__init__(None)

    def set_type(self, type_):
        if self.type is not None:
            raise TypeError('Field type is already set!')
        self.type = type_

    def get_proxy_fields(self):
        return {}

    def get_immutable(self, value, default_source):
        return value

    def get_mutable(self, value):
        return value


def give_none(self, *args, **kwargs):
    return None


frozenids_field = Field(FrozenIDs).set_name_and_model('ids', None)


class MetaModel(ABCMeta):
    """
    Metaclass for all choo models.
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(MetaModel, mcs).__new__(mcs, name, bases, attrs)
        if issubclass(cls, (Parser, tuple)):
            return cls

        fields = OrderedDict()
        fields.update(OrderedDict(sorted(
            [(n, v.set_name_and_model(n, cls)) for n, v in attrs.items() if isinstance(v, Field)],
            key=lambda v: v[1].i)
        ))

        for field in tuple(fields.values()):
            proxy_fields = field.get_proxy_fields()
            fields.update(proxy_fields)
            for name, field in proxy_fields.items():
                setattr(cls, name, field)

        for base in bases:
            fields.update(getattr(base, '_fields', {}))

        cls._fields = fields
        cls._nonproxy_fields = OrderedDict((n, v) for n, v in fields.items() if isinstance(v, Field))

        cls.NotFound = type('NotFound', (ObjectNotFound, ), {'__module__': attrs['__module__']})

        if mcs.__module__ != attrs['__module__'] and not issubclass(cls, Parser):
            from .sourced import SourcedModelMixin
            API._register_model(cls)
            cls.Sourced = type('Sourced'+cls.__name__, (SourcedModelMixin, cls),
                               {'__module__': cls.__module__, 'Model': cls})
            cls.XMLParser = type('XMLParser', (XMLParser, cls), {'__module__': cls.__module__, 'Model': cls})
            cls.JSONParser = type('JSONParser', (JSONParser, cls), {'__module__': cls.__module__, 'Model': cls})
        elif issubclass(cls, Parser) and Parser not in cls.__bases__:
            for name, field in cls._nonproxy_fields.items():
                if getattr(cls, name) is field:
                    setattr(cls, name, parser_property(give_none, name))

        return cls


class Model(Serializable, metaclass=MetaModel):
    Query = None

    def __init__(self, **kwargs):
        self._data = {}
        for name, field in self._nonproxy_fields.items():
            default = field.getdefault()
            if default is not None:
                self._data[name] = default

        for name, value in kwargs.items():
            # We access the field directly so it also works with Model.Sourced which prevents setting attributes
            field = self._fields.get(name)
            if field is None:
                raise AttributeError('%s model has no field %s' % (self.__class__.__name__, repr(name)))
            setattr(self, name, value)

    @classmethod
    def _get_serialized_type_name(cls):
        if cls in (Model, ModelWithIDs):
            return None
        return cls.__name__.lower()

    def _serialize(self, **kwargs):
        result = OrderedDict()

        for name, field in self._nonproxy_fields.items():
            value = field.serialize(getattr(self, name), **kwargs)
            if value is not None:
                result[name] = value

        return result

    def _sourced(self, source):
        return self.Sourced(source, **self._data)

    @classmethod
    def _unserialize(cls, data):
        kwargs = {}
        for name, value in data.items():
            field = cls._nonproxy_fields.get(name)
            if field is None:
                raise AttributeError('%s model has no field %s' % (cls.__name__, repr(name)))
            kwargs[name] = field.unserialize(value)
        return cls(**kwargs)


class ModelWithIDs(Model):
    ids = Field(IDs)

    def __eq__(self, other):
        from .sourced import SourcedModelMixin
        if not isinstance(other, ModelWithIDs):
            return False

        model1 = self.Model if isinstance(self, SourcedModelMixin) else self.__class__
        model2 = other.Model if isinstance(other, SourcedModelMixin) else other.__class__

        if model1 != model2:
            return False

        return bool(self.ids and other.ids and (self.ids & other.ids)) or None
