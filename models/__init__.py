#!/usr/bin/env python3
from .base import Serializable, Searchable, Collectable, TripPart
from .locations import Coordinates, AbstractLocation, Platform, Stop, Location, Address, POI
from .line import Line, LineType, LineTypes
from .trip import Trip
from .tickets import TicketList, TicketData
from .ride import Ride, RideSegment
from .way import Way, WayType
from .timeandplace import TimeAndPlace
from .realtime import RealtimeTime


def unserialize_typed(data):
    model, data = data
    if '.' in model:
        model = model.split('.')
        return getattr(globals()[model[0]], model[1]).unserialize(data)
    else:
        return globals()[model].unserialize(data)

__all__ = ['Serializable', 'Searchable', 'Collectable', 'TripPart',
           'Coordinates', 'AbstractLocation', 'Platform', 'Location', 'Stop',
           'Address', 'POI', 'Line', 'LineType', 'LineTypes', 'RealtimeTime',
           'TimeAndPlace', 'Platform', 'Ride', 'RideSegment', 'Trip', 'Way',
           'WayType', 'TicketList', 'TicketData', 'unserialize_typed']
