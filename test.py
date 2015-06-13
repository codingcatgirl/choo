#!/usr/bin/env python3
from networks import VRR
from models import Stop, Trip, unserialize_typed
from datetime import datetime
import json

vrr = VRR()
bs = Stop(city='essen', name='borbeck süd bf')
bo = Stop(city='essen', name='hbf')

trip = Trip.Request()
trip.origin = bs
trip.destination = bo

result = vrr.search_trips(trip)

#for trip in result:
#    print(trip)
#result = vrr.get_stop_rides(bs)
#result = vrr.get_stop_rides(bo)
#p = PrettyPrint()
#print(p.formatted(result))
#result.serialize(typed=True)
serialized = result.serialize(typed=True)
#unserialized = unserialize_typed(serialized)
#serialized2 = unserialized.serialize(typed=True)
#open('out1.json', 'w').write(json.dumps(serialized, indent=2, sort_keys=True))
#open('out2.json', 'w').write(json.dumps(serialized2, indent=2, sort_keys=True))
#print(serialized)
print(json.dumps(serialized, indent=2))
