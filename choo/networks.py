#!/usr/bin/env python3
from .apis.efa import EFA


class VRR(EFA):
    name = 'vrr'
    base_url = 'http://app.vrr.de/standard/'


class VRN(EFA):
    name = 'vrn'
    base_url = 'http://fahrplanauskunft.vrn.de/vrn/'


_names = {
    'vrr': VRR,
    'vrn': VRN,
}
supported = tuple(_names)


def network(name):
    global supported, _names
    if name not in supported:
        raise NameError('Unsupported network: %s' % name)
    return _names[name]
