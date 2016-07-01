from . import EFARequest
from ....models import POI, Platform, Stop
from ..parsers.coordinfo import CoordInfoGeoPoint


class CoordRequest(EFARequest):
    """
    Execute a COORDS_REQUEST (find Locations within a given distance from specific coordinates)
    """
    def __init__(self, api, coords, model_cls, max_distance, limit=None):
        super().__init__(api)

        post = {
            'language': 'de',
            'outputFormat': 'XML',
            'coordOutputFormat': 'WGS84',
            'inclFilter': '1',
            'coord': '%.6f:%.6f:WGS84' % reversed(coords),
        }

        if limit:
            post['max'] = limit

        types = []
        if issubclass(Stop, model_cls):
            types.append('STOP')

        if issubclass(POI, model_cls):
            types.append('POI_POINT')
            types.append('POI_AREA')

        if issubclass(Platform, model_cls):
            types.append('BUS_POINT')

        for i, type_ in enumerate(types):
            post.update({
                'type_%d' % (i+1): type_,
                'radius_%d' % (i+1): max_distance
            })

        xml = self._execute('XML_COORD_REQUEST', post)
        self.time = xml.attrib['now']

        data = xml.find('./itdCoordInfoRequest/itdCoordInfo/coordInfoItemList')
        self.results = (CoordInfoGeoPoint.parse(self, elem)
                        for elem in data.findall('./coordInfoItem'))
