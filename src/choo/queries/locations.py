from ..models import POI, Address, Location, Stop
from .base import Query


class LocationQuery(Query):
    Model = Location


class AddressQuery(Query):
    Model = Address


class StopQuery(Query):
    Model = Stop


class POIQuery(Query):
    Model = POI
