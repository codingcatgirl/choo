from .. import EFA
from ... import ParserError, cached_property, parser_property
from ....models import POI, Address, City, Stop
from ....types import Coordinates, FrozenIDs, StopIFOPT
from ...parsers import XMLParser


class OdvLocationList(EFA.Parser, XMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type, self.generator = self._parse_location(self.data)

    def _parse_location(self, data):
        """ Parse an ODV (OriginDestinationVia) XML node """
        odvtype = data.attrib['type']

        # Place.city
        p = data.find('./itdOdvPlace')
        cityid = None
        if p.attrib['state'] == 'empty':
            city = None
        elif p.attrib['state'] != 'identified':
            if p.attrib['state'] == 'list':
                return 'cities', (OdvPlaceElemCity(self, city) for city in p.find('./odvPlaceElem'))
            return 'none', ()
        else:
            city = p.find('./odvPlaceElem')

        # Location.name
        n = data.find('./itdOdvName')
        if n.attrib['state'] == 'empty':
            if city is not None:
                return 'cities', (city, )
            return 'none', ()

        if n.attrib['state'] == 'identified':
            ne = n.find('./odvNameElem')
            # AnyTypes are used in some EFA instances instead of ODV types
            odvtype = ne.attrib.get('anyType', odvtype)
            odvtype, location = self._parse_location_name(ne, city, cityid, odvtype)
            return odvtype, (location, )

        if n.attrib['state'] != 'list':
            return 'none', ()

        return 'mixed', (self._parse_location_name(item, city, cityid, odvtype)[1]
                         for item in sorted(n.findall('./odvNameElem'), reverse=True,
                                            key=lambda e: e.attrib.get('matchQuality', 0)))

    def _parse_location_name(self, data, city, cityid, odvtype):
        """ Parses the odvNameElem of an ODV """
        odvtype = data.attrib.get('anyType', odvtype)
        if odvtype == 'stop':
            return 'stop', OdvNameElemStop(self, data, city=city)
        elif odvtype == 'poi':
            return 'poi', OdvNameElemPOI(self, data, city=city)
        elif odvtype in ('street', 'singlehouse', 'coord', 'address'):
            return 'address', OdvNameElemAddress(self, data, city=city)
        else:
            raise ParserError(self, 'Unknown odvtype: %s' % odvtype)

    def __iter__(self):
        yield from self.generator


class OmcParserMixin:
    """
    Mixin for City parsers that have an omc xml attribute
    """
    @cached_property
    def _omc(self, data, **kwargs):
        self.api._parse_omc(data.attrib['omc'])

    @parser_property
    def country(self, data, country=None, **kwargs):
        return country if country else self._omc[0]

    @parser_property
    def state(self, data, **kwargs):
        return self._omc[1]

    @parser_property
    def official_id(self, data, **kwargs):
        return self._omc[2]


class OdvPlaceElemCity(OmcParserMixin, EFA.Parser, City.XMLParser):
    """
    Parse an <odvPlaceElem> Element into a City
    """
    @parser_property
    def ids(self, data, **kwargs):
        myid = data.attrib.get('stateless')
        return myid and FrozenIDs({self.api.name: myid})

    @parser_property
    def name(self, data, **kwargs):
        return data.text


class OdvNameElemCity(OmcParserMixin, EFA.Parser, City.XMLParser):
    """
    Parse the city part of an <odvNameElem> Element into a City
    """
    @parser_property
    def name(self, data, **kwargs):
        return data.attrib.get('locality')


class LocationParserMixin:
    """
    Mixin class for anything that parses an <odvNameElem> Element into a Location subclass
    """
    @parser_property
    def ids(self, data, **kwargs):
        myid = data.attrib.get('stopID') or data.attrib.get('id')
        return myid and FrozenIDs({self.api.name: myid})

    def _city_parse(self, data, city, country, **kwargs):
        if city is not None:
            return OdvPlaceElemCity(self, city, country=country)
        return OdvNameElemCity(self, data, country=country)

    @parser_property
    def city(self, data, city, **kwargs):
        return self._city_parse(data, city)

    @parser_property
    def name(self, data, **kwargs):
        return data.attrib.get('objectName', data.text)

    @parser_property
    def coords(self, data, **kwargs):
        if 'x' not in data.attrib:
            return None
        return Coordinates(float(data.attrib['y']) / 1000000,
                           float(data.attrib['x']) / 1000000)


class OdvNameElemAddress(EFA.Parser, Address.XMLParser, LocationParserMixin):
    """
    Parses an <odvNameElem> Element into an Address
    """
    @parser_property
    def street(self, data, **kwargs):
        return data.attrib.get('streetName')

    @parser_property
    def number(self, data, **kwargs):
        return data.attrib.get('buildingNumber') or data.attrib.get('houseNumber')

    @parser_property
    def postcode(self, data, **kwargs):
        return data.attrib.get('postCode')

    @parser_property
    def name(self, data, **kwargs):
        name = data.attrib.get('objectName', data.text)
        if name is not None:
            number = self.number
            if number and number not in name:
                name = '%s %s' % (name, number)
            return name
        return '%s %s' % (self.street, self.number)


class OdvNameElemStop(EFA.Parser, Stop.XMLParser, LocationParserMixin):
    """
    Parses an <odvNameElem> Element into a Stop
    """
    @parser_property
    def ifopt(self, data, **kwargs):
        return StopIFOPT.parse(data.attrib.get('gid') or None)

    @parser_property
    def city(self, data, city, **kwargs):
        ifopt = self.ifopt
        return self._city_parse(data, city, ifopt.country if ifopt else None)


class OdvNameElemPOI(EFA.Parser, POI.XMLParser, LocationParserMixin):
    """
    Parses an <odvNameElem> Element into an POI
    """
    pass
