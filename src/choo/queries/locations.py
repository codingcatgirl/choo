from ..models import POI, Address, Addressable, GeoPoint, Location, Platform, Stop
from .base import Query


class GeoPointQuery(Query):
    Model = GeoPoint
    _settings_defaults = {'max_distance': 1000}

    def max_distance(self, max_distance):
        if not isinstance(max_distance, int) or max_distance < 1:
            raise TypeError('max_distance has to be int > 0')
        self._update_setting('max_distance', max_distance)
        return self

    def __iter__(self):
        return self._full_iter() if self.coords is None else iter(way.destination for way in self._full_iter())

    def ways(self):
        if self.coords is None:
            raise TypeError('results are not available as ways because coords was not part of the query')
        return self._full_iter()


class PlatformQuery(GeoPointQuery):
    Model = Platform


class LocationQuery(GeoPointQuery):
    Model = Location


class AddressQuery(LocationQuery):
    Model = Address


class AddressableQuery(LocationQuery):
    Model = Addressable


class StopQuery(AddressableQuery):
    Model = Stop


class POIQuery(AddressableQuery):
    Model = POI
