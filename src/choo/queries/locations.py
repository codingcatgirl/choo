from ..models import POI, Address, Location, Stop
from .base import Query


class LocationQuery(Query):
    Model = Location
    _settings_defaults = {'max_distance': 1000}

    def max_distance(self, max_distance):
        if not isinstance(max_distance, int) or max_distance < 1:
            raise TypeError('max_distance has to be int > 0')
        self._update_setting('max_distance', max_distance)
        return self


class AddressQuery(Query):
    Model = Address


class StopQuery(Query):
    Model = Stop


class POIQuery(Query):
    Model = POI
