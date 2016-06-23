import json
import os
import sys

import defusedxml.ElementTree as ET
from defusedxml import minidom


class API:
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
    def __init__(self, parser, message):
        self.parser = parser
        self.message = message
        self.pretty_data = self.parser.printable_data()

        if os.environ.get('CHOO_DEBUG'):
            message += '\n'+self.pretty_data

        super().__init__(message)
        self.message = self.actual


class Parser:
    def __init__(self, parent, data, **kwargs):
        self.network = parent.network
        self.time = parent.time
        self.data = data
        self._kwargs = kwargs

    def printable_data(self, pretty=True):
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
    def printable_data(self, pretty=True):
        string = ET.tostring(self.data, 'utf-8')
        if pretty:
            string = minidom.parseString(string).toprettyxml(indent='  ')
        return string


class JSONParser(Parser):
    def printable_data(self, pretty=True):
        return json.dumps(self.data, indent=2 if pretty else None)


class parser_property(object):
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
    def wrapped_func(self):
        value = func(self, self.data, **self._kwargs)
        self.__dict__[func.__name__] = value
        return value
    return property(wrapped_func)
