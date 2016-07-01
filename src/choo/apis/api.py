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
            from .parsers import Parser
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

    @property
    def geopoints(self):
        raise NotImplementedError('Querying geopoints is not supported by this API.')

    @property
    def platforms(self):
        raise NotImplementedError('Querying platforms is not supported by this API.')

    @property
    def locations(self):
        raise NotImplementedError('Querying locations is not supported by this API.')

    @property
    def addresses(self):
        raise NotImplementedError('Querying addresses is not supported by this API.')

    @property
    def addressables(self):
        raise NotImplementedError('Querying addressables is not supported by this API.')

    @property
    def stops(self):
        raise NotImplementedError('Querying stops is not supported by this API.')

    @property
    def pois(self):
        raise NotImplementedError('Querying POIs is not supported by this API.')

    @property
    def trips(self):
        raise NotImplementedError('Querying trips is not supported by this API.')

    @classmethod
    def _register_query(cls, query_cls):
        if query_cls.Model in cls._supported_queries:
            raise TypeError('Duplicate %sQuery on %s API.' % (query_cls.Model.__name__, query_cls.API.__name__))
        cls._supported_queries[query_cls.Model] = query_cls

        setattr(cls, query_cls.Model.__name__.lower()+'s', property(lambda self: query_cls(self)))
