from ..models import POI, Address, Addressable, GeoPoint, Location, Platform, Stop
from .base import Query


class GeoPointQuery(Query):
    """
    A query for GeoPoint objects.

    Has a max_distance setting and a special ways iterator.
    """
    Model = GeoPoint
    _settings_defaults = {'max_distance': 1000}

    def max_distance(self, max_distance):
        """
        Set the maximum distance in meters from the given Coordinates (if the coord attribute is set).
        None means unlimited (although APIs can have an internal limit)
        """
        if not isinstance(max_distance, int) or max_distance < 1:
            raise TypeError('max_distance has to be int > 0')
        self._update_setting('max_distance', max_distance)
        return self

    def _execute(self):
        """
        See Query._execute() for details.

        If the coords attribute is set on the query, _execute() has to return Way instances
        with the result as their destination.
        """
        super()._execute()

    def __iter__(self):
        return self._full_iter() if self.coords is None else iter(way.destination for way in self._full_iter())

    def ways(self):
        """
        Only available if the coords attribute is set on the query.
        Return the results as Way instancess which have results as destinations.
        """
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
