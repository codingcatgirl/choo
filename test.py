#!/usr/bin/env python3
from networks import VRR
from models import Stop
from datetime import datetime

vrr = VRR()
du = Stop(city='Duisburg', name='hbf')
now = datetime.now()

result = vrr.get_stop_rides(du, now)
if type(result) == list:
    for a in result:
        print(a[0].__class__.__name__)
        print(a[0].__dict__)
else:
    print(result.__dict__)
    for a in result.rides:
        print(a.ride.__dict__)
