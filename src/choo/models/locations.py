from ..types import Coordinates, PlatformIFOPT, PlatformType, POIType, StopAreaIFOPT, StopIFOPT
from .base import Field, Model, ModelWithIDs


class GeoPoint(Model):
    """
    Anything that can have a geographic position.
    """
    def __init__(self, coords=None, **kwargs):
        super().__init__(**kwargs)
        self.coords = coords

    def distance_to(self, other):
        if not isinstance(other, GeoPoint):
            raise TypeError('distance_to expected GeoPoint object, not %s' % repr(other))

        if self.coords is None or other.coords is None:
            return None

        return self.coords.distance_do(other.coords)

    coords = Field(Coordinates)


class City(ModelWithIDs):
    country = Field(str)
    state = Field(str)
    official_id = Field(str)
    name = Field(str)

    def __init__(self, name=None, country=None, **kwargs):
        super().__init__(**kwargs)
        self.country = country
        self.name = name

    def __repr__(self):
        return '<%s: %s, %s, %s>' % (self.__class__.__name__, self.country, self.state, self.name)


class Location(GeoPoint):
    """
    A named stand-alone Location
    """
    city = Field(City, City)
    name = Field(str)

    def __init__(self, city=None, name=None, **kwargs):
        super().__init__(**kwargs)
        self.city = city
        self.name = name

    @property
    def country(self):
        return self.city__country

    def __repr__(self):
        return '<%s: %s, %s, %s>' % (self.__class__.__name__, self.country, self.city__name, self.name)


class Address(Location):
    street = Field(str)
    number = Field(str)
    postcode = Field(str)
    # near_stops = fields.Model('Stop.Results')

    def __repr__(self):
        return '<%s: %s-%s %s, %s>' % (self.__class__.__name__, self.country,
                                       self.postcode, self.city__name, self.name)


class Addressable(Location):
    address = Field(Address, Address)


class Stop(Addressable, ModelWithIDs):
    ifopt = Field(StopIFOPT)
    uic = Field(str)
    # rides = fields.Model('Ride.Results')
    # lines = fields.Model('Line.Results')

    def __init__(self, city=None, name=None, **kwargs):
        super().__init__(city=city, name=name, **kwargs)

    @property
    def country(self):
        return self.ifopt.country if self.ifopt else self.city__country


class POI(Addressable, ModelWithIDs):
    """
    A Point of Interest
    """
    poitype = Field(POIType)

    def __init__(self, city=None, name=None, **kwargs):
        super().__init__(city=city, name=name, **kwargs)

    def __repr__(self):
        return '<%s: %s, %s, %s, %s>' % (self.__class__.__name__, self.country, self.city__name,
                                         self.name, self.poitype)


class StopArea(ModelWithIDs):
    """
    A collection of platforms belonging to one particular stop
    """
    stop = Field(Stop, Stop)
    ifopt = Field(StopAreaIFOPT)
    name = Field(str)


class Platform(GeoPoint, ModelWithIDs):
    stop = Field(Stop, Stop)
    area = Field(StopArea, StopArea)
    ifopt = Field(PlatformIFOPT)
    platform_type = Field(PlatformType)
    name = Field(str)

    def __init__(self, stop=None, name=None, full_name=None, **kwargs):
        super().__init__(**kwargs)
        self.stop = stop
        self.name = name

    def __repr__(self):
        return '<%s: %s, %s, %s, %s>' % (self.__class__.__name__, repr(self.stop), self.name,
                                         self.platform_type, self.area__name)
