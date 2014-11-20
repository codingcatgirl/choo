#!/usr/bin/env python3
from datetime import datetime, timedelta


class Location():
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        self.country = country
        self.city = city
        self.name = name
        self.coords = coords


class Stop(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        Location.__init__(self, country, city, name, coords)
        self.rides = []


class POI(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        Location.__init__(self, country, city, name, coords)


class Address(Location):
    def __init__(self, country: str=None, city: str=None, name: str=None, coords: tuple=None):
        Location.__init__(self, country, city, name, coords)


class RealtimeTime():
    def __init__(self, time: datetime, delay: timedelta=None, livetime: datetime=None):
        if livetime is not None:
            if delay is not None:
                assert livetime-time == delay
            else:
                delay = livetime-time

        self.time = time
        self.delay = delay
        # self.islive
        # self.livetime


class TimeAndPlace():
    def __init__(self, stop: Stop, platform: str=None, arrival: RealtimeTime=None, departure: RealtimeTime=None):
        self.stop = stop
        self.platform = platform
        self.arrival = arrival
        self.departure = departure


class Line():
    pass


class Ride():
    def __init__(self, line: Line=None):
        self.stops = []
        self.line = line


class RideStopPointer():
    def __init__(self, i: int):
        self.i = i

    def __int__(self):
        return self.i


class RideSegment():
    def __init__(self, ride: Ride, origin: RideStopPointer=None, destination: RideStopPointer=None):
        self.ride = ride
        self.origin = origin
        self.destination = destination


class Way():
    def __init__(self, origin: Location, destination: Location, distance: int=None):
        self.origin = origin
        self.destination = destination
        self.distance = None
