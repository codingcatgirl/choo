#!/usr/bin/env python3
from apis.efa import EFA

supported = ('VRR', )


class VRR(EFA):
    name = 'vrr'
    base_url = 'http://app.vrr.de/standard/'
    country_by_id = (('2', 'de'), )
    ifopt_platforms = True
    ifopt_stopid_digits = 5

    def __init__(self):
        self.ids = {}
        self.raws = {}


def network(name):
    global supported
    if name not in supported:
        raise NameError('Unsupported network: %s' % name)
    return globals()[name]
