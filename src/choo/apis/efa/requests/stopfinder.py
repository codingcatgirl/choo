from datetime import datetime

from . import EFARequest, OdvParserMixin


class StopfinderRequest(EFARequest, OdvParserMixin):
    """
    Executes a STOPFINDER_REQUEST (which can not only find stops)
    """
    def __init__(self, api, location, coords=None, limit=None):
        super().__init__(api)
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

        if limit:
            post['anyMaxSizeHitList'] = limit

        if not post['place_sf']:
            post.pop('place_sf')

        xml = self._post('XML_STOPFINDER_REQUEST', post)
        self.time = datetime.strptime(xml.attrib['now'], '%Y-%m-%dT%H:%M:%S')

        data = xml.find('./itdStopFinderRequest')
        self.type, self.results = self._parse_odv(data.find('./itdOdv'))
