from .. import EFA
from ....models import POI, Address, GeoPoint, Stop, Way
from ....types import WayType
from ..requests.coord import CoordRequest
from ..requests.stopfinder import StopfinderRequest


class GeoPointQuery(EFA.GeoPointQueryBase):
    def _execute(self):
        if not self.coords:
            raise NotImplementedError('Not enough data for Query.')

        results = CoordRequest(api=self.api, coords=self.coords, model_cls=self.Model,
                               max_distance=self.settings['max_distance'], limit=self.settings['limit']).results
        return self._wrap_distance_results(results)

    def _wrap_distance_results(self, results):
        """
        Wraps results in Way objects and makes sure they are all within max_distance.
        """
        for result in results:
            if not result.coords:
                continue
            distance = self.coords.distance_to(result.coords)
            if distance <= self.settings['max_distance']:
                yield Way(waytype=WayType.walk, origin=GeoPoint(coords=self.coords),
                          destination=result, distance=distance)


class PlatformQuery(GeoPointQuery, EFA.PlatformQueryBase):
    def _execute(self):
        if self.stop:
            # Platforms of a specific stop are queried
            # This can only be done by querying all platforms near to the stop and filtering them
            # For this, we need the stop id and it's coordinates.
            stop = self.stop
            if not stop.coords or self.api.name not in self.ids:
                stop = self.api.stops.get(stop)
            if not stop.coords:
                raise NotImplementedError('Could not get stop coordinates needed to get its platforms.')

            results = (r for r in self.api.platforms.where(coords=stop.coords).max_distance(400) if r.stop == stop)
            return results if not self.coords else self._wrap_distance_results(results)
        else:
            return super()._execute()


class LocationQuery(GeoPointQuery, EFA.LocationQueryBase):
    def _execute(self):
        # Is this location unique by ID? If so, just query it.
        location = self._convert_unique_location()

        # If we have the name of the location or city, just query it
        if not location:
            location = {'type': 'any', 'place': self.city__name, 'name': self.name}

        # If we have coordinates, get the address nearest to them or just query all locations nearby
        if not location and self.coords:
            if self.Model == Address:
                location = {'type': 'coord', 'name': '%.6f:%.6f:WGS84' % reversed(self.coords)}

            if not location:
                return super()._execute()

        if not location:
            raise NotImplementedError('Not enough data for Query.')

        r = StopfinderRequest(api=self.api, location=location, limit=self.settings['limit'])

        if r.type == 'none':
            return ()
        elif r.type == 'stop':
            results = r.results if issubclass(Stop, self.Model) else ()
        elif r.type == 'address':
            results = r.results if issubclass(Address, self.Model) else ()
        elif r.type == 'poi':
            results = r.results if issubclass(POI, self.Model) else ()
        elif r.type == 'mixed':
            results = (r for r in r.results if isinstance(r, self.Model))

        return results if not self.coords else self._wrap_distance_results(results)

    def _convert_unique_location(self):
        """
        Return POST data for a STOPFINDER_REQUEST if a unique location is described by id, or else None.
        """
        return None


class AddressQuery(LocationQuery, EFA.AddressQueryBase):
    def _convert_unique_location(self):
        if self.ids and self.api.name in self.ids:
            return {'type': 'stop', 'place': None, 'name': str(self.ids[self.api.name])}
        if self.ifopt:
            return {'type': 'stop', 'place': None, 'name': '%s:%s:%s' % self.ifopt}
        return super()._convert_unique_location()


class AddressableQuery(LocationQuery, EFA.AddressableQueryBase):
    pass


class StopQuery(AddressableQuery, EFA.StopQueryBase):
    def _convert_unique_location(self):
        if self.ids and self.api.name in self.ids:
            return {'type': 'stop', 'place': None, 'name': str(self.ids[self.api.name])}
        if self.ifopt:
            return {'type': 'stop', 'place': None, 'name': '%s:%s:%s' % self.ifopt}
        return super()._convert_unique_location()


class POIQuery(AddressableQuery, EFA.POIQueryBase):
    def _convert_unique_location(self):
        if self.ids and self.api.name in self.ids:
            return {'type': 'poiID', 'name': str(self.ids[self.api.name])}
        return super()._convert_unique_location()
