from .. import EFA
from ... import cached_property, parser_property
from ....models import POI, Address, City, Stop
from ....types import Coordinates, FrozenIDs


class OmcParserMixin:
    """
    Mixin for City parsers that have an omc xml attribute
    """
    @cached_property
    def _omc(self, data, **kwargs):
        return self.api._parse_omc(data.attrib['omc'])

    @parser_property
    def ids(self, data, **kwargs):
        return FrozenIDs({self.country: self._omc[2]})

    @parser_property
    def country(self, data, country=None, **kwargs):
        return country if country else self._omc[0]

    @parser_property
    def state(self, data, **kwargs):
        return self._omc[1]


class OdvPlaceElemCity(OmcParserMixin, EFA.Parser, City.XMLParser):
    """
    Parse an <odvPlaceElem> Element into a City
    """
    @parser_property
    def ids(self, data, **kwargs):
        return super().ids | FrozenIDs({self.api.name: data.attrib.get('stateless')})

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

    def _city_parse(self, data, country, **kwargs):
        city = data.find('./odvPlaceElem')
        if city is not None:
            return OdvPlaceElemCity(self, city, country=country)
        return OdvNameElemCity(self, data, country=country)

    @parser_property
    def city(self, data,  **kwargs):
        return self._city_parse(data)

    @parser_property
    def name(self, data, **kwargs):
        return data.attrib.get('objectName', data.attrib.get('choo-text'))

    @parser_property
    def coords(self, data, **kwargs):
        if 'x' not in data.attrib:
            return None
        return Coordinates(float(data.attrib['y']) / 1000000,
                           float(data.attrib['x']) / 1000000)


class OdvNameElemAddress(LocationParserMixin, EFA.Parser, Address.XMLParser):
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


class OdvNameElemStop(LocationParserMixin, EFA.Parser, Stop.XMLParser):
    """
    Parses an <odvNameElem> Element into a Stop
    """
    @parser_property
    def ids(self, data, **kwargs):
        return super().ids | FrozenIDs({'ifopt': data.attrib.get('gid')})

    @parser_property
    def city(self, data, **kwargs):
        ifopt = self.ids.get('ifopt')
        return self._city_parse(data, ifopt.split(':', 1)[0] if ifopt else None)


class OdvNameElemPOI(LocationParserMixin, EFA.Parser, POI.XMLParser):
    """
    Parses an <odvNameElem> Element into an POI
    """
    pass
