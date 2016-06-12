#!/usr/bin/env python3
from choo.networks.de import vrr
from choo.models import Stop, City
import code

# collection = Collection('test')

bs = Stop(city=City('essen'), name='borbeck süd bf')
results = vrr.locations.where(city__name='essen', name='borbeck').execute()
code.interact(local=locals())


# bo = Stop(city='essen', name='hbf')
# bo = Stop(city='heidelberg', name='hbf')

# trip = Trip.Request()
# trip.origin = bs
# trip.destination = bo

# location = Location.Request()
# location.name = 'Borbeck'

# vrr.dump_raw = True
# result = vrr.query(trip)

# import pprint
# pp = pprint.PrettyPrinter(indent=1)
# pp.pprint(result.serialize())
# print(result.results)
# serialized = json.dumps(result.serialize(no_duplicates=[]), indent=2)
# print(serialized)
