#!/usr/bin/env python3
from .location import Coordinates, Location, Address, POI, Way
from .linetypes import LineType, LineTypes
from .realtime import RealtimeTime
from .main import Trip, Ride, TimeAndPlace, Line, Stop


def unserialize_typed(data):
    model, data = data
    if '.' in model:
        model = model.split('.')
        return getattr(globals()[model[0]], model[1]).unserialize(data)
    else:
        return globals()[model].unserialize(data)

__all__ = ['Coordinates', 'Location', 'Stop', 'Address', 'POI', 'Line',
           'LineType', 'LineTypes', 'RealtimeTime', 'TimeAndPlace', 'Ride',
           'Trip', 'Way', 'unserialize_typed']
