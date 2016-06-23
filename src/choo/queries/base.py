from collections import OrderedDict
from copy import deepcopy
from itertools import chain
from types import MappingProxyType

from ..models.base import Field, Model


class MetaQuery(type):
    def __new__(mcs, name, bases, attrs):
        not_field_attrs = {n: v for n, v in attrs.items() if not isinstance(v, Field)}
        cls = super(MetaQuery, mcs).__new__(mcs, name, bases, not_field_attrs)
        try:
            Model = attrs['Model']
        except KeyError:
            for base in bases:
                if hasattr(base, 'Model'):
                    Model = base.Model
                    break
            else:
                raise TypeError('Query without Model!')

        cls._fields = Model._fields

        cls._settings_defaults = OrderedDict()
        for base in cls.__bases__:
            cls._settings_defaults.update(getattr(base, '_settings_defaults', {}))
        if '_settings_defaults' in attrs:
            cls._settings_defaults.update(attrs['_settings_defaults'])

        return cls


class QuerySettingsProxy:
    def __init__(self, settings):
        self._settings = settings

    def __setattr__(self, name, value):
        if name != '_settings' or hasattr(self, name):
            raise TypeError('Can not set settings directly, set them using methods!')
        super().__setattr__(name, value)

    def __getattr__(self, name):
        try:
            return self._settings[name]
        except KeyError:
            raise AttributeError

    def __delattr__(self, name):
        raise TypeError


class Query(metaclass=MetaQuery):
    Model = Model
    _settings_defaults = {'limit': None}

    def __init__(self, network):
        if self.__class__ == Query:
            raise TypeError('only subclasses of Query can be initialised')

        self.network = network
        self._obj = self.Model()
        self._settings = self._settings_defaults.copy()
        self._cached_results = []
        self._results_generator = None
        self._results_done = False

    def copy(self):
        result = self.__class__(self.network)
        result._obj = deepcopy(self._obj)
        result._settings = self._settings
        return result

    def where(self, **kwargs):
        result = self.copy()

        for name, value in kwargs.items():
            if name not in self.Model._fields:
                raise TypeError('invalid field: %s.%s' % (self.Model.__name__, name))

            setattr(result._obj, name, value)

        return result

    @classmethod
    def unserialize(cls, data):
        raise NotImplementedError

    @property
    def settings(self):
        return MappingProxyType(self._settings)

    def get(self, obj):
        if not isinstance(obj, self.Model):
            raise TypeError('Expected %s instance, got %s' % (self.Model.__name__, repr(obj)))

        result = self.copy()
        result._obj = deepcopy(obj)
        r = result.limit(1).execute()
        if not r:
            raise self.Model.NotFound
        return next(iter(r))

    def _execute(self):
        raise TypeError('Cannot execute query not bound to a network')

    def limit(self, limit):
        if limit is not None and (not isinstance(limit, int) or limit < 1):
            raise TypeError('limit has to be None or int >= 1')
        self._update_setting('limit', limit)
        return self

    def _update_setting(self, name, value):
        result = self.copy()
        result._settings[name] = value
        return result

    def execute(self):
        if self._results_generator is None:
            self._results_generator = self._execute()
        return self

    def _full_iter(self):
        self.execute()

        if self._results_done:
            return iter(self._cached_results)

        return chain(self._cached_results, self._next_result())

    def __iter__(self):
        return self._full_iter

    def _next_result(self):
        for result in self._results_generator:
            self._cached_results.append(result)
            yield result
        self._results_done = True

    def __getattr__(self, name):
        if name in self.Model._fields:
            return getattr(self._obj, name)

        if name in self.__class__._settings_defaults:
            raise TypeError('Use .settings to get settings')

        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self.Model._fields:
            raise TypeError('Can not set fields, use .where()')

        if name in self._settings_defaults:
            raise TypeError('Can not set settings directly, set them using their methods')

        super().__setattr__(name, value)

    def __delattr__(self, name):
        if name in self.Model._fields:
            raise TypeError('Can not delete fields, use .where(%s=None)' % name)

        if name in self._settings_defaults:
            raise TypeError('Can not delete settings')

        super().__delattr__(name)
