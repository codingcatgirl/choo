from ....models import City, POI, Address, Location, Stop
from ....types import Coordinates, StopIFOPT
from ...base import ParserError, XMLParser, cached_property, parser_property


class OdvLocationList(XMLParser):
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
            return 'stop', OdvNameElemStop(self, data, city)
        elif odvtype == 'poi':
            return 'poi', OdvNameElemPOI(self, data, city)
        elif odvtype in ('street', 'singlehouse', 'coord', 'address'):
            return 'address', OdvNameElemAddress(self, data, city)
        else:
            raise ParserError(self, 'Unknown ofvtype: %s' % odvtype)

    def __iter__(self):
        yield from self.generator


class OdvPlaceElemCity(City.XMLParser):
    @parser_property
    def name(self, data, country=None):
        return data.text

    @cached_property
    def _omc(self, data, country=None):
        omc = data.attrib['omc']
        if self.network.preset == 'de':
            states = {'01': 'sh', '02': 'hh', '03': 'ni', '04': 'hb',
                      '05': 'nrw', '06': 'he', '07': 'rp', '08': 'bw',
                      '09': 'by', '10': 'sl', '11': 'be', '12': 'bb',
                      '13': 'mv', '14': 'sn', '15': 'st', '16': 'th'}
            tmp = omc.zfill(8)
            if len(tmp) == 8 and tmp[:2] in states:
                return 'de', states[tmp[:2]], tmp
            elif tmp.startswith('4'):
                return 'at', None, tmp[1:6]
            elif tmp.startswith('230'):
                return 'ch', None, None
            elif tmp.startswith('250'):
                return 'lu', None, None
            elif tmp.startswith('260'):
                return 'be', None, None
            elif tmp.startswith('270'):
                return 'nl', None, None
            elif tmp.startswith('18'):
                return 'pl', None, None
            elif tmp.startswith('55'):
                return 'cz', None, None
        return None, None, None

    @parser_property
    def country(self, data, country=None):
        return country if country else self._omc[0]

    @parser_property
    def state(self, data, country=None):
        return self._omc[1]

    @parser_property
    def official_id(self, data, country=None):
        return self._omc[2]


class OdvNameElemLocation(Location.XMLParser):
    @parser_property
    def ids(self, data, city):
        myid = data.attrib.get('stopID') or data.attrib.get('id')
        return myid and {self.network.name: myid}

    def _city_parse(self, data, city, country=None):
        if city is not None:
            return OdvPlaceElemCity(self, city, country=country)

        city = data.attrib.get('locality')
        return City(name=city, country=country) if city else None

    @parser_property
    def city(self, data, city):
        return self._city_parse(data, city)

    @parser_property
    def name(self, data, city):
        return data.attrib.get('objectName', data.text)

    @parser_property
    def coords(self, data, city):
        if 'x' not in data.attrib:
            return None
        return Coordinates(float(data.attrib['y']) / 1000000,
                           float(data.attrib['x']) / 1000000)


class OdvNameElemAddress(Address.XMLParser, OdvNameElemLocation):
    @parser_property
    def street(self, data, city):
        return data.attrib.get('streetName')

    @parser_property
    def number(self, data, city):
        return data.attrib.get('buildingNumber') or data.attrib.get('houseNumber')

    @parser_property
    def postcode(self, data, city):
        return data.attrib.get('postCode')

    @parser_property
    def name(self, data, city):
        name = data.attrib.get('objectName', data.text)
        if name is not None:
            number = self.number
            if number and number not in name:
                name = '%s %s' % (name, number)
            return name
        return '%s %s' % (self.street, self.number)


class OdvNameElemStop(Stop.XMLParser, OdvNameElemLocation):
    @parser_property
    def ifopt(self, data, city):
        return StopIFOPT.parse(data.attrib.get('gid') or None)

    @parser_property
    def city(self, data, city):
        ifopt = self.ifopt
        return self._city_parse(data, city, ifopt.country if ifopt else None)


class OdvNameElemPOI(POI.XMLParser, OdvNameElemLocation):
    pass
