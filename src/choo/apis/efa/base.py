from .. import API, ParserError
from ...types import PlatformType, POIType


class EFA(API):
    poitype_mapping = (
        ('A', POIType.education),
        ('B', POIType.public_building),
        ('D', POIType.graveyard),
        ('F', POIType.sport),
        ('JC', POIType.place_of_worship),
        ('J', POIType.sight),
        ('K', POIType.venue),
        ('NC', POIType.parking),
        ('ND', POIType.bicycle_hire),
        ('U', POIType.mall),
    )
    platformtype_mapping = {
        'Bay': PlatformType.street,
        'Platform': PlatformType.platform,
        '': PlatformType.unknown,
    }

    def __init__(self, name, base_url, preset):
        super().__init__(name)
        self.base_url = base_url
        self.preset = preset

    def _parse_omc(self, omc):
        """
        Parse omc data (part of a city) into country, state and official city id
        """
        if self.preset == 'de':
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

    def _parse_poitype(self, ident):
        """
        Parse a COORD_REQUEST POI type by its identifier
        """
        for n, poitype in self.poitype_mapping:
            if ident.startswith(n):
                return poitype
        return POIType.unknown

    def _parse_platformtype(self, ident):
        """
        Parse a COORD_REQUEST platform type by its CHARACTERISTICS attribute
        """
        try:
            return self.platformtype_mapping[ident]
        except KeyError:
            raise ParserError('Unknown Platform Characteristic')
