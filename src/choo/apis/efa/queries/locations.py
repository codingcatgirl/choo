from .... import queries
from ....models import POI, Address, Stop
from ..parsers.locations import OdvLocationList


class LocationQueryExecuter:
    def _execute(self):
        post = {
            'language': 'de',
            'outputFormat': 'XML',
            'coordOutputFormat': 'WGS84',
            'locationServerActive': 1,
            # 'regionID_sf': 1, // own region
            'SpEncId': 0,
            'odvSugMacro': 'true',
            'useHouseNumberList': 'true',
        }
        post.update(self.network._convert_location(self, '%s_sf'))

        xml, self.time = self.network._request('XML_STOPFINDER_REQUEST', post)
        data = xml.find('./itdStopFinderRequest')

        results = OdvLocationList(self, data.find('./itdOdv'))
        if results.type == 'none':
            return ()
        elif results.type == 'stop':
            return results if issubclass(Stop, self.Model) else ()
        elif results.type == 'address':
            return results if issubclass(Address, self.Model) else ()
        elif results.type == 'poi':
            return results if issubclass(POI, self.Model) else ()
        if results.type == 'mixed':
            return (r for r in results if isinstance(r, self.Model))

        return ()


class LocationQuery(LocationQueryExecuter, queries.LocationQuery):
    pass


class AddressQuery(LocationQueryExecuter, queries.AddressQuery):
    pass


class StopQuery(LocationQueryExecuter, queries.StopQuery):
    pass


class POIQuery(LocationQueryExecuter, queries.POIQuery):
    pass
