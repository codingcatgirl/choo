#!/usr/bin/env python3
from networks import VRR
from models import Stop, Trip, TripRequest
from datetime import datetime
from output import PrettyPrint
import json

vrr = VRR()
du = Stop(city='essen', name='hbf')
bs = Stop(city='essen', name='borbeck süd bf')

trip = TripRequest()
trip.origin = bs
trip.destination = du

result = vrr.search_trips(trip)
#result = vrr.get_stop_rides(bs)
p = PrettyPrint()
print(p.formatted(result))
#print(json.dumps(result.serialize(), indent=2))
