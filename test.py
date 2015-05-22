#!/usr/bin/env python3
from networks import VRR
from models import Stop, Trip, unserialize_typed
from datetime import datetime
from output import PrettyPrint
import json

vrr = VRR()
bs = Stop(city='essen', name='borbeck süd bf')
bo = Stop(city='essen', name='borbeck bf')

trip = Trip.Request()
trip.origin = bs
trip.destination = bo

#result = vrr.search_trips(trip)
result = vrr.get_stop_rides(bs)
#result = vrr.get_stop_rides(bo)
#p = PrettyPrint()
#print(p.formatted(result))
print(json.dumps(result.serialize(typed=True), indent=2))
