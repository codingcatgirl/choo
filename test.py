#!/usr/bin/env python3
from networks import VRR
from models import Stop
from datetime import datetime
from output import PrettyPrint
import json

vrr = VRR()
<<<<<<< HEAD
du = Stop(city='essen', name='hbf')
=======
du = Stop(city='essen', name='borbeck süd bf')
>>>>>>> 2b6f041581cb63bbf168ee9f5d5482a7ae93e245

result = vrr.get_stop_rides(du)
p = PrettyPrint()
print(p.formatted(result))
# print(json.dumps(result.serialize(), indent=2))
