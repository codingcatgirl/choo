#!/usr/bin/env python3
from .location import Coordinates, Location, Address, POI, Way
from .linetypes import LineType, LineTypes
from .realtime import RealtimeTime
from .main import Trip, Ride, TimeAndPlace, Line, Stop

def unserialize_typed():
    return globals()[data[0]].unserialize(data[1])

__all__ = ['Coordinates', 'Location', 'Stop', 'Address', 'POI', 'Line',
           'LineType', 'LineTypes', 'RealtimeTime', 'TimeAndPlace', 'Ride',
           'Trip', 'Way', 'unserialize_typed']
