from ...requests import XMLRequest
from ..parsers.odv import OdvPlaceElemCity, OdvNameElemPOI, OdvNameElemStop, OdvNameElemAddress
from ... import ParserError

from copy import deepcopy


class EFARequest(XMLRequest):
    def _url_filter(self, endpoint):
        return self.api.base_url + endpoint


class OdvParserMixin:
    def _parse_odv(self, data):
        """
        Parse an ODV (OriginDestinationVia) XML node
        """
        odvtype = data.attrib['type']

        # Place.city
        p = data.find('./itdOdvPlace')
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
            odvtype, location = self._parse_location_name(ne, city, odvtype)
            return odvtype, (location, )

        if n.attrib['state'] != 'list':
            return 'none', ()

        return 'mixed', (self._parse_location_name(item, city, odvtype)[1]
                         for item in sorted(n.findall('./odvNameElem'), reverse=True,
                                            key=lambda e: e.attrib.get('matchQuality', 0)))

    def _parse_location_name(self, data, city, odvtype):
        """
        Parses the odvNameElem of an ODV
        """
        data = deepcopy(data)
        data.attrib['choo-text'] = data.text
        if city is not None:
            data.append(city)
        odvtype = data.attrib.get('anyType', odvtype)
        if odvtype == 'stop':
            return 'stop', OdvNameElemStop(self, data)
        elif odvtype == 'poi':
            return 'poi', OdvNameElemPOI(self, data)
        elif odvtype in ('street', 'singlehouse', 'coord', 'address'):
            return 'address', OdvNameElemAddress(self, data)
        else:
            raise ParserError(self, 'Unknown odvtype: %s' % odvtype)
