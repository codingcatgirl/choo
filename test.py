#!/usr/bin/env python3
from networks import VRR
from models import Stop
from datetime import datetime

vrr = VRR()
du = Stop(city='essen', name='berlin')

result = vrr._stop_finder_request(du)
for stop in result:
    print(stop)
