from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from copy import deepcopy
from itertools import chain
from types import MappingProxyType
from ..types import Serializable


class MetaQuery(ABCMeta):
    """
    Metaclass for all Queries
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(MetaQuery, mcs).__new__(mcs, name, bases, attrs)
        try:
            Model = attrs['Model']
        except KeyError:
            for base in bases:
                if hasattr(base, 'Model'):
                    Model = base.Model
                    break
            else:
                raise TypeError('Query without Model!')

        if Model is not None:
            Model.Query = cls

        cls._settings_defaults = OrderedDict()
        for base in cls.__bases__:
            cls._settings_defaults.update(getattr(base, '_settings_defaults', {}))
        if '_settings_defaults' in attrs:
            cls._settings_defaults.update(attrs['_settings_defaults'])

        return cls


class QuerySettingsProxy:
    """
    Proxy for Query settings that allows read-only access (used bei Query.settings)
    """
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


class Query(Serializable, metaclass=MetaQuery):
    """
    A Query for a specific Model.

    A Query has settings and all attributes of its model.
    Neither of these values ever change. All methods by which the query can be altered return a new query.
    It can be executed using .execute() or by accessing its results like an iterable.
    """
    Model = None
    _settings_defaults = {'limit': None}

    def __init__(self, api):
        if self.__class__ == Query:
            raise TypeError('only subclasses of Query can be initialised')

        if isinstance(self, BoundAPIQuery):
            if not isinstance(api, self.API):
                raise ValueError('api has to be an %s subclass, got %s instead' % repr(self.API), repr(api))
        else:
            if api is not None:
                raise ValueError('api has to be None, got %s instead.' % repr(api))

        self.api = api
        self._obj = self.Model()
        self._settings = self._settings_defaults.copy()
        self._cached_results = []
        self._results_generator = None
        self._results_done = False

    def copy(self):
        """
        Returns a deep copy of the query.
        """
        result = self.__class__(self.api)
        result._obj = deepcopy(self._obj)
        result._settings = self._settings
        return result

    def where(self, **kwargs):
        """
        Returns a new Query with the Model attributes updated.

        Example:
        >>> query.where(name='Berlin Hbf').execute()
        """
        result = self.copy()

        for name, value in kwargs.items():
            if name not in self.Model._fields:
                raise TypeError('invalid field: %s.%s' % (self.Model.__name__, name))

            setattr(result._obj, name, value)

        return result

    @classmethod
    def _full_class_name(cls):
        return 'queries.%s' % (cls.Model.__name__ if cls.Model else 'Query')

    def _serialize(self):
        return OrderedDict((
            ('api', self.api.serialize() if self.api else None),
            ('obj', self._obj.serialize()),
            ('settings', self._settings),
        ))

    @classmethod
    def _unserialize(cls, data):
        from ..apis.base import API
        api = API.unserialize(data.get('api'))
        if issubclass(cls, BoundAPIQuery) or api is None:
            result = cls(api)
        else:
            result = getattr(api, cls.Model.__name__.lower()+'s')
        result = cls(API.unserialize(data.get('api')))
        result._obj = cls.Model.unserialize(data.get('obj', {}))
        for name, value in data.get('settings', {}).items():
            result = getattr(result, name)(value)
        return result

    @property
    def settings(self):
        """
        Returns the current query settings as a read-only QuerySettingsProxy object.

        Example:
        >>> query.settings.limit
        """
        return MappingProxyType(self._settings)

    def get(self, obj):
        """
        Retrieve the given object from the API.
        Returns the retrieved object or raises Model.NotFound.

        Example:
        >>> try:
        ...     query.get(Stop(name='Essen Hbf'))
        ... except Stop.NotFound:
        ...     pass
        """
        if not isinstance(obj, self.Model):
            raise TypeError('Expected %s instance, got %s' % (self.Model.__name__, repr(obj)))

        result = self.copy()
        result._obj = deepcopy(obj)
        r = result.limit(1).execute()
        if not r:
            raise self.Model.NotFound
        return next(iter(r))

    def _execute(self):
        """
        This is the only method that an APIs should overwrite.
        It has to return iterable (or generator) over instances of the query's model.
        Some Query types (e.g. GeoLocationQuery) require different result types.
        """
        raise TypeError('Cannot execute query not bound to an API')

    def limit(self, limit):
        """
        Set the maximum number of results. Returns a new query.
        None means unlimited (although APIs can have an internal limit)
        """
        if limit is not None and (not isinstance(limit, int) or limit < 1):
            raise TypeError('limit has to be None or int >= 1')
        self._update_setting('limit', limit)
        return self

    def _update_setting(self, name, value):
        result = self.copy()
        result._settings[name] = value
        return result

    def execute(self):
        """
        Execute the query. Returns the query itself.
        If the Query was already executed, nothing happens.
        """
        if self._results_generator is None:
            self._results_generator = self._execute()
        return self

    def _full_iter(self):
        """
        Returns an iterator over the query results.
        Used by __iter__() which is overwritten by some Queries which supply metadata, like any GeoPointQuery.
        """
        self.execute()

        if self._results_done:
            return iter(self._cached_results)

        return chain(self._cached_results, self._next_result())

    def __iter__(self):
        """
        Iterate over the query results. Each item is _alwayss_ a subclass of the query's Model.
        """
        return self._full_iter

    def _next_result(self):
        """
        Iterate over the results generator. Used by _full_iter().
        """
        for result in self._results_generator:
            self._cached_results.append(result)
            yield result
        self._results_done = True

    def __getattr__(self, name):
        """
        Deliver attribute values of the underlying object.
        """
        if name in self.Model._fields:
            return getattr(self._obj, name)

        if name in self.__class__._settings_defaults:
            raise TypeError('Use .settings to get settings')

        raise AttributeError(name)

    def __setattr__(self, name, value):
        """
        Raise correct exceptions if someone tries to set settings or model attributes.
        """
        if name in self.Model._fields:
            raise TypeError('Can not set fields, use .where()')

        if name in self._settings_defaults:
            raise TypeError('Can not set settings directly, set them using their methods')

        super().__setattr__(name, value)

    def __delattr__(self, name):
        """
        Raise correct exceptions if some tries to delete settings or model attributes.
        """
        if name in self.Model._fields:
            raise TypeError('Can not delete fields, use .where(%s=None)' % name)

        if name in self._settings_defaults:
            raise TypeError('Can not delete settings')

        super().__delattr__(name)


class MetaBoundAPIQuery(MetaQuery, ABCMeta):
    pass


class BoundAPIQuery(Query, metaclass=MetaBoundAPIQuery):
    API = None

    @abstractmethod
    def _execute(self):
        pass
