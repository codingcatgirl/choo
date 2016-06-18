from .... import queries
from ....models import POI, Address, GeoPoint, Stop, Way
from ....types import WayType
from ..parsers.locations import OdvLocationList


class LocationQueryExecuter:
    def _execute(self):
        location = self._convert_unique_location()
        if location:
            return self._stopfinder_request(location)

        if self.coords:
            if self.Model == Stop:
                return self._coordinates_request()
            if self.Model == Address:
                return self._stopfinder_request({'type': 'coord', 'name': '%.6f:%.6f:WGS84' %
                                                (self.coords.lon, self.coords.lat)})
        return self._stopfinder_request({'type': 'any', 'place': self.city__name, 'name': self.name})

    def _stopfinder_request(self, location):
        # Executes a STOPFINDER_REQUEST (which can not only find stops)
        post = {
            'language': 'de',
            'outputFormat': 'XML',
            'coordOutputFormat': 'WGS84',
            'locationServerActive': 1,
            # 'regionID_sf': 1, # own region
            'SpEncId': 0,
            'odvSugMacro': 'true',
            'useHouseNumberList': 'true',
            'type_sf': location['type'],
            'place_sf': location['place'],
            'name_sf': location['name']
        }

        if not post['place_sf']:
            post.pop('place_sf')

        xml, self.time = self.network._request('XML_STOPFINDER_REQUEST', post)
        data = xml.find('./itdStopFinderRequest')

        results = OdvLocationList(self, data.find('./itdOdv'))
        if results.type == 'none':
            return ()
        elif results.type == 'stop':
            results = results if issubclass(Stop, self.Model) else ()
        elif results.type == 'address':
            results = results if issubclass(Address, self.Model) else ()
        elif results.type == 'poi':
            results = results if issubclass(POI, self.Model) else ()
        elif results.type == 'mixed':
            results = (r for r in results if isinstance(r, self.Model))

        return results if not self.coords else self._filter_stopfinder_results(results)

    def _filter_stopfinder_results(self, results):
        for result in results:
            if not result.coords:
                continue
            distance = self.coords.distance_to(result.coords)
            if distance > self.settings.max_distance:
                yield Way(waytype=WayType.walk, origin=GeoPoint(self.coords), destination=result, distance=distance)

    def _coordinates_request(self):
        # Executes as COORDS_REQUEST (which can only find stops)
        pass


class LocationQuery(LocationQueryExecuter, queries.LocationQuery):
    def _convert_unique_location(self):
        return None


class AddressQuery(LocationQueryExecuter, queries.AddressQuery):
    pass


class StopQuery(LocationQueryExecuter, queries.StopQuery):
    def _convert_unique_location(self):
        if self.ids and self.network.name in self.ids:
            return {'type': 'stop', 'place': None, 'name': str(self.ids[self.network.name])}
        if self.ifopt:
            return {'type': 'stop', 'place': None, 'name': '%s:%s:%s' % self.ifopt}
        return super()._convert_location()
    pass


class POIQuery(LocationQueryExecuter, queries.POIQuery):
    def _convert_unique_location(self):
        if self.ids and self.network.name in self.ids:
            return {'type': 'poiID', 'name': str(self.ids[self.network.name])}
        return super()._convert_location()
    pass
