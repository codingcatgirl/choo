#!/usr/bin/env python3
# flake8: noqa
import code
import json  # noqa
from pprint import pprint  # noqa

from choo.apis import vrr
from choo.models import City, Stop
from choo.queries import PlatformQuery  # noqa
from choo.types import Coordinates, Serializable  # noqa

# collection = Collection('test')

# query = vrr.stops.where(city__name='Duisburg', name='A')
query = vrr.platforms.where(stop__name='Essen Borbeck Süd').limit(1)
result = list(query)[0]
for result in list(query)[:1]:
    print(json.dumps(result.serialize(by_reference=True), ensure_ascii=False, indent=2))
print(result.stop is result.area.stop)

# result = vrr.stops.get(bs)
# result
# print(json.dumps(query.serialize(), indent=2))
# PlatformQuery.unserialize(query.serialize())

# results = query.execute()
#
# pprint(list(results)[0].serialize())
# result = list(results)[0]
# print(json.dumps(result.mutable().serialize(), indent=2))
# print(json.dumps(Serializable.unserialize(result.serialize()).serialize(), indent=2))
# pprint(Serializable.subclasses)
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
