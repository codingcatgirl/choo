from abc import ABCMeta
from collections import OrderedDict

from typing import Optional

from ..apis.base import JSONParser, Parser, XMLParser, parser_property
from ..exceptions import ObjectNotFound
from ..types import IDs, Serializable


class Field:
    """
    A field on a choo model.
    Each field has a type and validates it when a value is set.
    """
    _i = 0

    def __init__(self, types, model=None):
        self.types = Optional[types]
        self.Model = model
        self.i = Field._i
        Field._i += 1

    def set_name(self, name):
        self.name = name
        return self

    def validate(self, value):
        return issubclass(type(value), self.types)

    def serialize(self, value):
        return value.serialize() if isinstance(value, Serializable) else value

    def get_proxy_fields(self):
        if self.Model is None:
            return OrderedDict()
        return OrderedDict(((self.name+'__'+name, ProxyField(self, name)) for name in self.Model._fields.keys()))

    def proxy_set(self, obj, name, value):
        subobj = getattr(obj, self.name)
        if subobj is None:
            subobj = self.Model()
            setattr(obj, self.name, subobj)

        setattr(subobj, name, value)

    def proxy_get(self, obj, name):
        subobj = getattr(obj, self.name)
        return None if subobj is None else getattr(subobj, name)

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return obj._data.get(self.name)

    def __set__(self, obj, value):
        if not self.validate(value):
            raise TypeError('Invalid type for attribute %s.' % self.name)
        obj._data[self.name] = value


class ProxyField:
    """
    A proxy field on a choo model (e.g. Stop.city__name)
    """
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def set_name(self, name):
        self.name = name
        return self

    def validate(self, value):
        return issubclass(type(value), self.types)

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return self.parent.proxy_get(obj, self.name)

    def __set__(self, obj, value):
        return self.parent.proxy_set(obj, self.name, value)


def give_none(self, *args, **kwargs):
    return None


class MetaModel(ABCMeta):
    """
    Metaclass for all choo models.
    """
    def __new__(mcs, name, bases, attrs):
        fields = OrderedDict()
        fields.update(OrderedDict(sorted(
            [(n, v.set_name(n)) for n, v in attrs.items() if isinstance(v, Field)],
            key=lambda v: v[1].i)
        ))

        for field in tuple(fields.values()):
            proxy_fields = field.get_proxy_fields()
            fields.update(proxy_fields)
            attrs.update(proxy_fields)

        for base in bases:
            fields.update(getattr(base, '_fields', {}))

        attrs['_fields'] = fields
        attrs['_nonproxy_fields'] = OrderedDict((n, v) for n, v in fields.items() if isinstance(v, Field))

        cls = super(MetaModel, mcs).__new__(mcs, name, bases, attrs)
        cls.NotFound = type('NotFound', (ObjectNotFound, ), {'__module__': attrs['__module__']})

        if not issubclass(cls, Parser):
            cls.XMLParser = type('XMLParser', (XMLParser, cls), {'__module__': attrs['__module__'], 'Model': cls})
            cls.JSONParser = type('JSONParser', (JSONParser, cls), {'__module__': attrs['__module__'], 'Model': cls})
        elif Parser not in sum([b.__bases__ for b in cls.__bases__], ()):
            for name, field in cls._nonproxy_fields.items():
                if getattr(cls, name) is field:
                    setattr(cls, name, parser_property(give_none, name))

        return cls


class Model(Serializable, metaclass=MetaModel):
    Query = None

    @classmethod
    def _full_class_name(cls):
        return super()._full_class_name() if issubclass(cls, Parser) else ('models.%s' % cls.__name__)

    def __init__(self):
        self._data = {}

    def _serialize(self):
        result = OrderedDict()
        for name, field in self._nonproxy_fields.items():
            value = field.serialize(getattr(self, name))
            if value is not None:
                result[name] = field.serialize(getattr(self, name))
        return result

    @classmethod
    def _unserialize(self, data):
        raise NotImplementedError


class ModelWithIDs(Model):
    ids = Field(IDs)

    def __eq__(self, other):
        if not isinstance(other, ModelWithIDs):
            return False

        model1 = self.Model if isinstance(self, Parser) else self.__class__
        model2 = other.Model if isinstance(other, Parser) else other.__class__

        if model1 != model2:
            return False

        print(self.ids, other.ids)

        return (self.ids and other.ids and self.ids & other.ids) or None
