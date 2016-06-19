from ....models import City, GeoPoint, Platform, POI, Stop
from ....types import Coordinates, StopIFOPT, PlatformIFOPT
from ...base import XMLParser, ParserError, cached_property, parser_property
from .utils import GenAttrMapping


class CoordInfoGeoPointList(XMLParser):
    def __iter__(self):
        return (CoordInfoGeoPoint.parse(self, elem) for elem in self.data.findall('./coordInfoItem'))


class CoordInfoGeoPoint(GeoPoint.XMLParser):
    @classmethod
    def parse(cls, parent, data):
        type_ = data.attrib['type']
        if type_ == 'STOP':
            return CoordInfoStop(parent, data)
        elif type_ in ('POI_POINT', 'POI_AREA'):
            return CoordInfoPOI(parent, data)
        elif type_ in ('BUS_POINT'):
            return CoordInfoPlatform(parent, data)
        else:
            raise ParserError(parent, 'Unknown coordInfoItem type: %s' % type_)


class GeoPointParserMixin:
    @parser_property
    def coords(self, data):
        coords = data.find('./itdPathCoordinates/itdCoordinateBaseElemList/itdCoordinateBaseElem')
        return Coordinates(int(coords.find('./y').text)/1000000, int(coords.find('./x').text)/1000000)

    @cached_property
    def _attrs(self, data):
        return GenAttrMapping(data.find('./genAttrList'))


class LocationParserMixin(GeoPointParserMixin):
    @parser_property
    def name(self, data):
        return data.attrib.get('name', '').strip() or None


class CoordInfoLocationCity(City.XMLParser):
    @cached_property
    def _omc(self, data, country=None):
        return self.network._parse_omc(data.attrib['omc'])

    @parser_property
    def country(self, data, country=None):
        return country if country else self._omc[0]

    @parser_property
    def state(self, data, country=None):
        return self._omc[1]

    @parser_property
    def official_id(self, data, country=None):
        return self._omc[2]

    @parser_property
    def name(self, data, country=None):
        return data.attrib['locality']

    @parser_property
    def ids(self, data, city):
        myid = data.attrib.get('omc')+':'+data.attrib.get('placeID')
        return myid and {self.network.name: myid}


class CoordInfoStop(LocationParserMixin, Stop.XMLParser):
    @parser_property
    def ifopt(self, data):
        return StopIFOPT.parse(self._attrs.get('STOP_GLOBAL_ID'))

    @parser_property
    def city(self, data):
        ifopt = self.ifopt
        return CoordInfoLocationCity(self, data, ifopt.country if ifopt else None)


class CoordInfoPOI(LocationParserMixin, POI.XMLParser):
    @parser_property
    def city(self, data):
        return CoordInfoLocationCity(self, data, None)


class CoordInfoPlatform(GeoPointParserMixin, Platform.XMLParser):
    @parser_property
    def ifopt(self, data):
        return PlatformIFOPT.parse(self._attrs.get('STOPPOINT_GLOBAL_ID'))

    @parser_property
    def stop(self, data):
        return CoordInfoStop(self, data)

    @parser_property
    def name(self, data):
        return self._attrs.get('IDENTIFIER')
