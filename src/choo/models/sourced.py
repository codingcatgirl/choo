from collections import OrderedDict
from operator import itemgetter

from ..apis import API
from ..apis.parsers import Parser
from .base import MetaModel, Model, ModelWithIDs


class SourcedModelMixinMeta(MetaModel, type):
    def __new__(mcs, name, bases, attrs):
        cls = super(SourcedModelMixinMeta, mcs).__new__(mcs, name, bases, attrs)

        if issubclass(cls, Model):
            cls.source = property(itemgetter(0))

            for i, (name, field) in enumerate(cls._nonproxy_fields.items(), start=1):
                setattr(cls, name, property(itemgetter(i)))

        return cls


class SourcedModelMixin(tuple, metaclass=SourcedModelMixinMeta):
    __slots__ = ()

    def __new__(cls, source, **kwargs):
        if cls is SourcedModelMixin:
            raise TypeError('SourcedModelMixin cannot be initialized directly')

        if not isinstance(source, API):
            raise TypeError('source argument has to be an API instance, not %s' % repr(source))

        args = [source]

        for name, field in cls._nonproxy_fields.items():
            args.append(field.get_immutable(kwargs.pop(name, None), default_source=source))

        for name in kwargs:
            raise TypeError('Unknown attribute %s' % repr(name))

        return tuple.__new__(cls, args)

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        return ('<from %s: ' % self.source.serialize())+self.Model.__repr__(self)+'>'

    @classmethod
    def from_parser(cls, parser):
        if not isinstance(parser, Parser):
            raise TypeError('%s.Sourced: parser has to be a Parser instance, not %s' %
                            (cls.Model.__name__, repr(parser)))

        return cls.from_object(parser.api, parser)

    @classmethod
    def from_object(cls, source, obj):
        if not isinstance(obj, cls.Model):
            raise ValueError('%s.Sourced: obj has to be a %s instance, not %s' %
                             (cls.Model.__name__, cls.Model.__name__, repr(obj)))

        kwargs = {name: getattr(obj, name, None) for name, field in cls._nonproxy_fields.items()}
        return cls(source=source, **kwargs)

    def mutable(self):
        kwargs = dict(zip(self._nonproxy_fields.keys(), tuple(self)[1:]))
        return self.Model(**kwargs)

    def sourced(self):
        return self

    def _call_recursive(self, func):
        for name in self._nonproxy_fields:
            value = getattr(self, name)
            if isinstance(value, Model):
                value._call_recursive(func)
        func(self)

    def __eq__(self, other):
        return self.Model.__eq__(self, other)

    def _apply_recursive(self, func):
        kwargs = {}
        for name in self._nonproxy_fields:
            value = getattr(self, name)
            if isinstance(value, Model):
                kwargs[name] = value._apply_recursive(func)
            else:
                kwargs[name] = value
        return func(self.Model.Sourced(**kwargs))

    def _serialize(self, **kwargs):
        data = OrderedDict({'source': self.source.serialize(**kwargs)})
        data.update(super()._serialize(**kwargs))
        return data

    @classmethod
    def _unserialize(cls, data):
        data = data.copy()
        source = API.unserialize(data.pop('source', None))
        kwargs = {}
        for name, value in data.items():
            field = cls._nonproxy_fields.get(name)
            if field is None:
                raise AttributeError('%s model has no field %s' % (cls.__name__, repr(name)))
            kwargs[name] = field.unserialize(value)
        return cls(source, **kwargs)

    def combine(self, other):
        if not isinstance(other, self.Model.Sourced):
            raise TypeError('Can only combine with another Model.Sourced instance, got %s instead' % repr(other))

        if self.source != other.source:
            raise NotImplementedError('Combining Model.Sourced instances from different sources is not supported yet!')

        kwargs = {}
        changed = False
        for name, field in self._nonproxy_fields.items():
            value = getattr(self, name)
            other_value = getattr(other, name)
            if other_value is None:
                kwargs[name] = value
                continue

            if issubclass(field.type, Model):
                other_value = other_value if value is not other_value else None
            elif isinstance(self, ModelWithIDs) and name == 'ids':
                other_value = (other_value | value) if value != other_value else None
            else:
                other_value = other_value if value != other_value else None

            kwargs[name] = other_value if other_value is not None else value
            changed = changed or other_value is not None

        return self.Model.Sourced(source=self.source, **kwargs) if changed else self

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
