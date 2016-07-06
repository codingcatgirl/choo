from .. import EFA
from ... import ParserError, cached_property, parser_property
from ....models import POI, City, GeoPoint, Platform, Stop, StopArea
from ....types import Coordinates, FrozenIDs
from .utils import GenAttrMapping


class CoordInfoGeoPoint(EFA.Parser, GeoPoint.XMLParser):
    """
    Parse <coordInfoItem> into its correct GeoPoint submodel
    """
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
    """
    Mixin for any <coordInfoItem> parser
    """
    @parser_property
    def coords(self, data, no_coords=False, **kwargs):
        if no_coords:
            return None
        coords = data.find('./itdPathCoordinates/itdCoordinateBaseElemList/itdCoordinateBaseElem')
        return Coordinates(int(coords.find('./y').text)/1000000, int(coords.find('./x').text)/1000000)

    @cached_property
    def _attrs(self, data, **kwargs):
        """
        Get <genAttrList> attributes
        """
        return GenAttrMapping(data.find('./genAttrList'))


class LocationParserMixin(GeoPointParserMixin):
    """
    Mixin for any <coordInfoItem> parser for Location submodels
    """
    @parser_property
    def name(self, data, **kwargs):
        return data.attrib.get('name', '').strip() or None


class CoordInfoLocationCity(EFA.Parser, City.XMLParser):
    """
    Parse the city part of a <coordInfoItem> into a City
    """
    @parser_property
    def ids(self, data, **kwargs):
        return FrozenIDs({
            self.api.name: ('placeID:'+data.attrib['omc']+':'+data.attrib['placeID']
                            if 'placeID' in data.attrib else None),
            self.country: self._omc[2]
        })

    @cached_property
    def _omc(self, data, **kwargs):
        return self.api._parse_omc(data.attrib['omc'])

    @parser_property
    def country(self, data, country=None, **kwargs):
        return country if country else self._omc[0]

    @parser_property
    def state(self, data, **kwargs):
        return self._omc[1]

    @parser_property
    def name(self, data, **kwargs):
        return data.attrib['locality']


class CoordInfoStop(LocationParserMixin, EFA.Parser, Stop.XMLParser):
    """
    Parse a <coordInfoItem> that describes a Stop
    """
    @parser_property
    def ids(self, data, platform=None, **kwargs):
        return FrozenIDs({
            self.api.name: platform.ids[self.api.name].split('-')[0] if platform else data.attrib.get('id'),
            'ifopt': self._attrs.get('STOP_GLOBAL_ID')
        })

    @parser_property
    def city(self, data, **kwargs):
        ifopt = self.ids.get('ifopt')
        return CoordInfoLocationCity(self, data, country=ifopt.split(':')[0] if ifopt else None)


class CoordInfoPOI(LocationParserMixin, EFA.Parser, POI.XMLParser):
    """
    Parse a <coordInfoItem> that describes a POI
    """
    @parser_property
    def city(self, data, **kwargs):
        return CoordInfoLocationCity(self, data)

    @parser_property
    def poitype(self, data, **kwargs):
        key = max(self._attrs.getall('POI_HIERARCHY_KEY'), key=lambda x: len(x), default=None)
        return self.api._parse_poitype(key)


class CoordInfoPlatform(GeoPointParserMixin, EFA.Parser, Platform.XMLParser):
    """
    Parse a <coordInfoItem> that describes a Platform
    """
    @parser_property
    def ids(self, data, **kwargs):
        return FrozenIDs({
            self.api.name: data.attrib.get('id'),
            'ifopt': self._attrs.get('STOPPOINT_GLOBAL_ID')
        })

    @parser_property
    def stop(self, data, **kwargs):
        return CoordInfoStop(self, data, platform=self, no_coords=True)

    @parser_property
    def name(self, data, **kwargs):
        return self._attrs.get('STOP_POINT_LONGNAME', '').strip() or self._attrs.get('IDENTIFIER')

    @parser_property
    def area(self, data, **kwargs):
        return CoordInfoStopArea(self, data, platform=self)

    @parser_property
    def platform_type(self, data, **kwargs):
        return self.api._parse_platformtype(self._attrs.get('STOP_POINT_CHARACTERISTICS'))


class CoordInfoStopArea(GeoPointParserMixin, EFA.Parser, StopArea.XMLParser):
    """
    Parse a the stop area part pf <coordInfoItem> that describes a Platform into a StopArea
    """
    @parser_property
    def ids(self, data, platform):
        myid = platform.ids.get(self.api.name)
        ifopt = platform.ids.get('ifopt')
        return FrozenIDs({
            self.api.name: '-'.join(myid.split('-')[:2]) if myid else None,
            'ifopt': ':'.join(ifopt.split(':')[:4]) if ifopt else None
        })

    @parser_property
    def stop(self, data, platform):
        return platform.stop

    @parser_property
    def name(self, data, platform):
        return platform._attrs.get('STOP_AREA_NAME', '').strip() or None
