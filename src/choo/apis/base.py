import json
import os
import sys
from abc import ABC, ABCMeta, abstractmethod
from collections import OrderedDict, deque
from datetime import datetime

import defusedxml.ElementTree as ET
from defusedxml import minidom

from ..types import Serializable, SimpleSerializable

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


class ParserError(Exception):
    """
    Exception raised if data can not be parsed.

    The parser attribute contains the Parser in which the error occured.
    The pretty_data attribute contains the parser's data as a string.
    """
    def __init__(self, parser, message):
        self.parser = parser
        self.message = message
        self.pretty_data = self.parser.printable_data()

        if os.environ.get('CHOO_DEBUG'):
            message += '\n'+self.pretty_data

        super().__init__(message)


class Parser(Serializable, ABC):
    """
    A object that parses data, usually into model attributes.
    Only subclasses of this class (XMLParser, JSONParser) may be used directly.

    The data attribute contains the data.
    The api attribute contains the API instance which supplied the data.
    The time attribute contains the time of the data as datetime.

    If you want to implement a parser that describes a Model attributes, start similar to this:
    >>> class MyStopParser(Stop.XMLParser):
    >>>     @parser_property
    ...     def name(self, data, **kwargs):
    ...         pass  # Do your parsing
    Your parser may also inherit from another one of your parsers instead.

    Model attributes that are not implemented by your parser automatically will return None.
    """
    API = None

    def __init__(self, parent, data, api=None, time=None, **kwargs):
        """
        Initialise the parser.
        parent has to be an object from which the api and time attributes can be taken.
        data is the parser's data.
        Any additional keyword arguments will be forwarded to all parser_property and cached_property methods.
        """
        if self.API is None:
            raise TypeError('Use the API.Parser mixin. Example: class MyStop(EFA.Parser, Stop.XMLParser):')

        self.__dict__['source'] = self.__dict__['api'] = api if api else parent.api
        self.__dict__['time'] = time if time else parent.time
        self.data = data
        self._kwargs = kwargs

    @abstractmethod
    def printable_data(self, pretty=True):
        """
        Get the parsers data as string.
        if pretty is True, the data is made easy-readable for humans (e.g. by indenting)
        """
        pass

    def sourced(self, deep=True):
        return self.Model.Sourced(self, deep)

    @classmethod
    @abstractmethod
    def _parse_raw_data(cls, data):
        pass

    @classmethod
    def parse(cls, api, time, data, **kwargs):
        result = cls(None, cls._parse_raw_data(data), api=api, time=time, **kwargs)
        if not isinstance(api, cls.API):
            raise TypeError('Wrong API for this parser. Expected %s subclass, not %s.' % (repr(cls.API), repr(api)))
        return result

    @classmethod
    def _get_serialized_type_name(cls):
        from ..models import Model
        if issubclass(cls, Model) and cls.API is not None:
            return (cls.Model.__name__.lower()+'.parser.'+cls.__module__).replace('.choo.apis.', '.')+cls.__name__

    def _serialize(self):
        result = OrderedDict((
            ('api', self.api.serialize()),
            ('time', self.time.isoformat()),
            ('data', self.printable_data(pretty=False).decode()),
            ('kwargs', self._kwargs),
        ))
        kwargs = {}
        for name, value in self._kwargs.items():
            kwargs[name] = value.serialize() if isinstance(value, Serializable) else value
        result['kwargs'] = kwargs
        return result

    @classmethod
    def _unserialize(cls, data):
        kwargs = data['kwargs']
        for name, value in list(kwargs.items()):
            if isinstance(value, dict) and '@type' in value:
                kwargs[name] = Serializable.unserialize(value)
        return cls.parse(API.unserialize(data['api']), datetime.strptime(data['time'], '%Y-%m-%dT%H:%M:%S'),
                         data['data'], **kwargs)

    def __setattr__(self, name, value):
        if name in getattr(self, '_nonproxy_fields', ()):
            raise TypeError('Cannot set a parser property')
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if name in getattr(self, '_nonproxy_fields', ()):
            raise TypeError('Cannot delete a parser property')
        super().__delattr__(name)


class XMLParser(Parser):
    """
    A Parser that parses XML using defusedxml.ElementTree.
    data has to be a defusedxml.ElementTree.Element instance, e.g. ElementTree.fromstring(…).
    """
    def printable_data(self, pretty=True):
        string = ET.tostring(self.data, 'utf-8')
        if pretty:
            string = minidom.parseString(string).toprettyxml(indent='  ')
        return string

    @classmethod
    def _parse_raw_data(cls, data):
        return ET.fromstring(data)


class JSONParser(Parser):
    """
    A Parser that parses JSON.
    data has to be json serializable, e.g. json.loads(…).
    """
    def printable_data(self, pretty=True):
        return json.dumps(self.data, indent=2 if pretty else None)

    @classmethod
    def _parse_raw_data(cls, data):
        return json.loads(data)


class parser_property(object):
    """
    A decorator to create a parser property that describes a model attribute.

    The name of the property has to be a the name of a field of the given model.

    The underlying method gets called with the parser's data as a additional positional argument
    and all additional keyword arguments that the parser was initialized with. It will only be
    called once as it's return value will be cached.

    If an exception is raised from your method, debug info will be added to its message.

    Example:
    >>> class MyStopParser(Stop.XMLParser):
    >>>     @parser_property
    ...     def name(self, data, **kwargs):
    ...         pass  # Do your parsing
    """
    def __init__(self, func, name=None):
        self.func = func
        self.name = name or func.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self

        field = obj.Model._fields[self.name]
        try:
            value = obj.__dict__[self.name] = self.func(obj, obj.data, **obj._kwargs)
        except Exception as e:
            raise type(e)(str(e) +
                          '\n\n### CHOO DEBUG INFO:\n%s' % obj.printable_data()).with_traceback(sys.exc_info()[2])

        if not field.validate(value):
            raise TypeError('Invalid type for attribute %s.' % self.name)

        return value


def cached_property(func):
    """
    A decorator to create an internal parser property that does not correspond to a field of the given model.
    The name of the property should start with an underscore.

    This decorator is similar to parser_property, but it only caches the result and adds the method arguments.
    There is no exception handling.
    """
    def wrapped_func(self):
        value = func(self, self.data, **self._kwargs)
        self.__dict__[func.__name__] = value
        return value
    return property(wrapped_func)
