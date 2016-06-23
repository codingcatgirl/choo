import json
import os
import sys

import defusedxml.ElementTree as ET
from defusedxml import minidom


class API:
    """
    An API subclass is a collection of Query implementations used by different networks.
    The instance of an API has a name and is usually a network.

    To start a query on an API instance use its properties:
    >>> api.stops.where(name='Essen')
    This may raise a NotImplementedError if the API does not implement this Query.
    """
    GeoPointQuery = None
    PlatformQuery = None
    LocationQuery = None
    AddressQuery = None
    AddressableQuery = None
    StopQuery = None
    POIQuery = None
    TripQuery = None

    def __init__(self, name):
        if self.__class__ == API:
            raise TypeError('Only API subclasses can be initialized.')
        self.name = name

    @property
    def geopoints(self):
        if self.GeoPointQuery is None:
            raise NotImplementedError('Querying geopoints is not supported by this network.')
        return self.GeoPointQuery(self)

    @property
    def platforms(self):
        if self.PlatformQuery is None:
            raise NotImplementedError('Querying platforms is not supported by this network.')
        return self.PlatformQuery(self)

    @property
    def locations(self):
        if self.LocationQuery is None:
            raise NotImplementedError('Querying locations is not supported by this network.')
        return self.LocationQuery(self)

    @property
    def addresses(self):
        if self.AddressQuery is None:
            raise NotImplementedError('Querying addresses is not supported by this network.')
        return self.AddressQuery(self)

    @property
    def addressables(self):
        if self.AddressableQuery is None:
            raise NotImplementedError('Querying addressables is not supported by this network.')
        return self.AddressableQuery(self)

    @property
    def stops(self):
        if self.StopQuery is None:
            raise NotImplementedError('Querying stops is not supported by this network.')
        return self.StopQuery(self)

    @property
    def pois(self):
        if self.POIQuery is None:
            raise NotImplementedError('Querying POIs is not supported by this network.')
        return self.POIQuery(self)

    @property
    def trips(self):
        if self.TripQuery is None:
            raise NotImplementedError('Querying trips is not supported by this network.')
        return self.TripQuery(self)


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


class Parser:
    """
    A object that parses data, usually into model attributes.
    Only subclasses of this class (XMLParser, JSONParser) may be used directly.

    The data attribute contains the data.
    The network property contains the API instance which supplied the data.
    The time attribute contains the time of the data as datetime.

    If you want to implement a parser that describes a Model attributes, start similar to this:
    >>> class MyStopParser(Stop.XMLParser):
    >>>     @parser_property
    ...     def name(self, data, **kwargs):
    ...         pass  # Do your parsing
    Your parser may also inherit from another one of your parsers instead.

    Model attributes that are not implemented by your parser automatically will return None.
    """
    def __init__(self, parent, data, **kwargs):
        """
        Initialise the parser.
        parent has to be an object from which the network and time properties can be taken.
        data is the parser's data.
        Any additional keyword arguments will be forwarded to all parser_property and cached_property methods.
        """
        self.network = parent.network
        self.time = parent.time
        self.data = data
        self._kwargs = kwargs

    def printable_data(self, pretty=True):
        """
        Get the parsers data as string.
        if pretty is True, the data is made easy-readable for humans (e.g. by indenting)
        """
        raise NotImplementedError

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


class JSONParser(Parser):
    """
    A Parser that parses JSON.
    data has to be json serializable, e.g. json.loads(…).
    """
    def printable_data(self, pretty=True):
        return json.dumps(self.data, indent=2 if pretty else None)


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
