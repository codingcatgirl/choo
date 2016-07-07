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

    def __init__(self, type_):
        self.type = type_
        self.i = Field._i
        Field._i += 1

    def set_name(self, name):
        self.name = name
        return self

    def validate(self, value):
        return value is None or isinstance(value, self.type)

    def serialize(self, value, _id_lookup, **kwargs):
        if isinstance(value, Serializable):
            if _id_lookup is not None and isinstance(value, Model):
                return _id_lookup(value)
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

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return self.parent.proxy_get(obj, self.name)

    def __set__(self, obj, value):
        return self.parent.proxy_set(obj, self.name, value)


def give_none(self, *args, **kwargs):
    return None


frozenids_field = Field(FrozenIDs).set_name('ids')


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

        if 'ids' in fields and SourcedModelMixin in bases:
            attrs['ids'] = fields['ids'] = frozenids_field

        attrs['_fields'] = fields
        attrs['_nonproxy_fields'] = OrderedDict((n, v) for n, v in fields.items() if isinstance(v, Field))

        cls = super(MetaModel, mcs).__new__(mcs, name, bases, attrs)
        cls.NotFound = type('NotFound', (ObjectNotFound, ), {'__module__': attrs['__module__']})

        if mcs.__module__ != attrs['__module__'] and not issubclass(cls, (Parser, SourcedModelMixin)):
            API._register_model(cls)
            cls.Sourced = type('Sourced'+name, (SourcedModelMixin, cls), {'__module__': cls.__module__, 'Model': cls})
            cls.XMLParser = type('XMLParser', (XMLParser, cls.Sourced), {'__module__': cls.__module__})
            cls.JSONParser = type('JSONParser', (JSONParser, cls.Sourced), {'__module__': cls.__module__})
        elif issubclass(cls, Parser) and Parser not in cls.__bases__:
            for name, field in cls._nonproxy_fields.items():
                if getattr(cls, name) is field:
                    setattr(cls, name, parser_property(give_none, name))

        return cls


class Model(Serializable, metaclass=MetaModel):
    Query = None

    def __init__(self, **kwargs):
        self._data = {}
        for name, value in kwargs.items():
            # We access the field directly so it also works with Model.Sourced which prevents setting attributes
            field = self._fields.get(name)
            if field is None:
                raise AttributeError('%s model has no field %s' % (self.__class__.__name__, repr(name)))
            field.__set__(self, value)

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

    @classmethod
    def _unserialize(cls, data):
        kwargs = {}
        for name, value in data.items():
            field = cls._nonproxy_fields.get(name)
            if field is None:
                raise AttributeError('%s model has no field %s' % (cls.__name__, repr(name)))
            kwargs[name] = field.unserialize(value)
        return cls(**kwargs)


class SourcedModelMixin(Model):
    source = Field(API)

    def __init__(self, **kwargs):
        if self.__class__ is SourcedModelMixin:
            raise TypeError('SourcedModelMixin cannot be initialized directly')

        super().__init__(**kwargs)

        if kwargs.get('source') is None:
            raise ValueError('SourcedModel.source has to be set!')

    @classmethod
    def from_parser(cls, parser, deep=True):
        if not isinstance(parser, cls.Model.Sourced):
            raise ValueError('%s.Sourced: parser has to be a %s.Sourced instance, not %s' %
                             (cls.Model.__name__, cls.Model.__name__, repr(parser)))

        kwargs = {}
        for name, field in cls._nonproxy_fields.items():
            value = getattr(parser, name)
            if isinstance(value, Parser) and deep:
                value = value.sourced(deep)
            kwargs[name] = value
        return cls(**kwargs)

    def mutable(self, deep=True):
        kwargs = {}
        for name, field in self.Model._nonproxy_fields.items():
            value = getattr(self, name)
            if isinstance(value, SourcedModelMixin) and deep:
                value = value.mutable(deep)
            kwargs[name] = value
        return self.Model(**kwargs)

    def _call_recursive(self, func):
        for name in self._nonproxy_fields:
            value = getattr(self, name)
            if isinstance(value, SourcedModelMixin):
                value._call_recursive(func)
        func(self)

    def _apply_recursive(self, func):
        kwargs = {}
        for name in self._nonproxy_fields:
            value = getattr(self, name)
            if isinstance(value, SourcedModelMixin):
                kwargs[name] = value._apply_recursive(func)
            else:
                kwargs[name] = value
        return func(self.Model.Sourced(**kwargs))

    def sourced(self, deep=True):
        return self.Model.Sourced.from_parser(self, deep)

    def combine(self, *others):
        for other in others:
            if not isinstance(other, self.Model.Sourced):
                raise TypeError('Can only combine with another Model.Sourced instance, got %s instead' % repr(other))

        objects_by_source = {}
        for obj in (self, )+others:
            objects_by_source.setdefault(obj.source, []).append(obj)

        if len(objects_by_source) > 1:
            raise NotImplementedError('Combining Model.Sourced instances from different sources is not supported yet!')

        # get fields to merge
        defaults = {}
        if isinstance(self, ModelWithIDs):
            defaults['ids'] = FrozenIDs()

        for source, objects in objects_by_source.items():
            kwargs = defaults.copy()
            for name in self._nonproxy_fields:
                if name == 'ids' and isinstance(self, ModelWithIDs):
                    kwargs['ids'] |= (getattr(self, 'ids') or FrozenIDs())
                    continue

                for obj in objects:
                    value = getattr(self, name)
                    if value is not None:
                        break
                kwargs[name] = value
            return self.Model.Sourced(**kwargs)

    def __or__(self, other):
        return self.combine(other)

    @classmethod
    def _get_serialized_type_name(cls):
        if cls in (Model, ModelWithIDs, SourcedModelMixin):
            return None
        return cls.Model._get_serialized_type_name()+'.sourced'

    def __setattr__(self, name, value):
        if name in getattr(self, '_nonproxy_fields', ()):
            raise TypeError('Cannot set a Model.Sourced property')
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if name in getattr(self, '_nonproxy_fields', ()):
            raise TypeError('Cannot delete a Model.Sourced property')
        super().__delattr__(name)

Model.Sourced = SourcedModelMixin


class ModelWithIDs(Model):
    ids = Field(IDs)

    def __eq__(self, other):
        if not isinstance(other, ModelWithIDs):
            return False

        model1 = self.Model if isinstance(self, SourcedModelMixin) else self.__class__
        model2 = other.Model if isinstance(other, SourcedModelMixin) else other.__class__

        if model1 != model2:
            return False

        return bool(self.ids and other.ids and (self.ids & other.ids)) or None
