from abc import ABCMeta
from collections import deque

from ..types import SimpleSerializable

_apis_by_name = {}


class MetaAPI(ABCMeta):
    """
    Meta Class for APIs. It creates the BoundAPIQuery helpers.
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(MetaAPI, mcs).__new__(mcs, name, bases, attrs)

        # Only create the helpers on subclasses of API
        if mcs.__module__ != attrs['__module__']:
            from ..queries.base import Query, BoundAPIQuery
            from ..caches import DefaultCache
            from .parsers import Parser
            cls._default_cache = DefaultCache
            cls.Query = type('Query', (BoundAPIQuery, ), {'__module__': attrs['__module__'], 'API': cls})
            cls.Parser = type('Parser', (Parser, ), {'__module__': attrs['__module__'], 'API': cls})
            cls._supported_queries = {}
            base_queries = deque(q for q in Query.__subclasses__() if not issubclass(q, BoundAPIQuery))
            while base_queries:
                base_query = base_queries.popleft()
                base_queries.extend(q for q in base_query.__subclasses__() if not issubclass(q, BoundAPIQuery))
                setattr(cls, base_query.__name__+'Base', type(base_query.__name__+'Base', (cls.Query, base_query, ),
                                                              {'__module__': attrs['__module__']}))
        return cls

    @property
    def supported_queries(cls):
        return frozenset(cls._supported_queries)


class API(SimpleSerializable, metaclass=MetaAPI):
    """
    An API subclass is a collection of Query implementations used by different networks.
    The instance of an API has a name and is usually a network.

    To start a query on an API instance use its properties:
    >>> api.stops.where(name='Essen')
    This may raise a NotImplementedError if the API does not implement this Query.
    """
    _model_to_query = {}

    def __init__(self, name):
        if self.__class__ == API:
            raise TypeError('Only API subclasses can be initialized.')
        if name in _apis_by_name:
            raise TypeError('Duplicate API name: %s' % name)

        self.name = name
        _apis_by_name[name] = self

    @classmethod
    def _get_serialized_type_name(cls):
        return 'api'

    @classmethod
    def _model_to_plural_name(cls, model):
        name = model.__name__
        return {'City': 'cities', 'POI': 'POIs', 'Address': 'addresses'}.get(name, name.lower()+'s')
        pass

    @classmethod
    def _register_model(cls, model):
        name = cls._model_to_plural_name(model)
        error = 'Querying '+name+' is not supported by this API.'

        def api_func(self):
            return self._query(model, APIWithCache(self, self._default_cache()), error)
        api_func.__name__ = name.lower()

        def api_with_cache_func(self):
            return self.api._query(model, self, error)
        api_with_cache_func.__name__ = name.lower()

        setattr(API, name.lower(), property(api_func))
        setattr(APIWithCache, name.lower(), property(api_with_cache_func))

    def start_model_query(self, model):
        return getattr(self, self._model_to_plural_name(model))

    def _simple_serialize(self):
        return self.name

    @classmethod
    def _simple_unserialize(cls, data):
        if data is None:
            return None
        try:
            return _apis_by_name[data]
        except:
            raise ValueError('API %s does not exist!' % data)

    def _query(self, model, api_with_cache, error):
        query = self._supported_queries.get(model)
        if query is None:
            raise NotImplementedError(error)
        return query(api_with_cache)

    @classmethod
    def _register_query(cls, query_cls):
        if query_cls.Model in cls._supported_queries:
            raise TypeError('Duplicate %sQuery on %s API.' % (query_cls.Model.__name__, query_cls.API.__name__))
        cls._supported_queries[query_cls.Model] = query_cls


class APIWithCache:
    def __init__(self, api, cache=None):
        self.api = api
        self.cache = cache
