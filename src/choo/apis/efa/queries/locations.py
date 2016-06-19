from .... import queries
from ....models import POI, Address, GeoPoint, Platform, Stop, Way
from ....types import WayType
from ..parsers.coordinfo import CoordInfoGeoPointList
from ..parsers.odv import OdvLocationList


class GeoPointQuery(queries.GeoPointQuery):
    def _execute(self):
        if not self.coords:
            raise NotImplementedError('Not enough data for Query.')

        return self._coordinates_request()

    def _coordinates_request(self):
        # Executes as COORDS_REQUEST
        post = {
            'language': 'de',
            'outputFormat': 'XML',
            'coordOutputFormat': 'WGS84',
            'inclFilter': '1',
            'coord': '%.6f:%.6f:WGS84' % reversed(self.coords),
        }

        if self.settings['limit']:
            post['max'] = self.settings['limit']

        types = []
        if issubclass(Stop, self.Model):
            types.append('STOP')

        if issubclass(POI, self.Model):
            types.append('POI_POINT')
            types.append('POI_AREA')

        if issubclass(Platform, self.Model):
            types.append('BUS_POINT')

        for i, type_ in enumerate(types):
            post.update({
                'type_%d' % (i+1): type_,
                'radius_%d' % (i+1): self.settings['max_distance']
            })

        xml, self.time = self.network._request('XML_COORD_REQUEST', post)
        data = xml.find('./itdCoordInfoRequest')

        results = CoordInfoGeoPointList(self, data.find('./itdCoordInfo/coordInfoItemList'))
        return self._wrap_distance_results(results)

    def _wrap_distance_results(self, results):
        for result in results:
            if not result.coords:
                continue
            distance = self.coords.distance_to(result.coords)
            if distance > self.settings['max_distance']:
                yield Way(waytype=WayType.walk, origin=GeoPoint(self.coords), destination=result, distance=distance)


class PlatformQuery(GeoPointQuery, queries.PlatformQuery):
    pass


class LocationQuery(GeoPointQuery, queries.LocationQuery):
    def _execute(self):
        location = self._convert_unique_location()
        if location:
            return self._stopfinder_request(location)

        if not self.coords or self.city__name or self.name:
            return self._stopfinder_request({'type': 'any', 'place': self.city__name, 'name': self.name})

        if self.coords:
            if self.Model == Address:
                return self._stopfinder_request({'type': 'coord', 'name': '%.6f:%.6f:WGS84' % reversed(self.coords)})
            return self._coordinates_request()

        raise NotImplementedError('Not enough data for Query.')

    def _convert_unique_location(self):
        return None

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
            'name_sf': location['name'],
        }

        if self.settings['limit']:
            post['anyMaxSizeHitList'] = self.settings['limit']

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

        return results if not self.coords else self._wrap_distance_results(results)


class AddressQuery(LocationQuery, queries.AddressQuery):
    def _convert_unique_location(self):
        if self.ids and self.network.name in self.ids:
            return {'type': 'stop', 'place': None, 'name': str(self.ids[self.network.name])}
        if self.ifopt:
            return {'type': 'stop', 'place': None, 'name': '%s:%s:%s' % self.ifopt}
        return super()._convert_location()


class AddressableQuery(LocationQuery, queries.AddressableQuery):
    pass


class StopQuery(AddressableQuery, queries.StopQuery):
    def _convert_unique_location(self):
        if self.ids and self.network.name in self.ids:
            return {'type': 'stop', 'place': None, 'name': str(self.ids[self.network.name])}
        if self.ifopt:
            return {'type': 'stop', 'place': None, 'name': '%s:%s:%s' % self.ifopt}
        return super()._convert_location()


class POIQuery(AddressableQuery, queries.POIQuery):
    def _convert_unique_location(self):
        if self.ids and self.network.name in self.ids:
            return {'type': 'poiID', 'name': str(self.ids[self.network.name])}
        return super()._convert_location()
