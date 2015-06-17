#!/usr/bin/env python3
from apis.efa import EFA


class VRR(EFA):
    name = 'vrr'
    base_url = 'http://app.vrr.de/standard/'
    country_by_id = (('2', 'de'), )
    ifopt_platforms = True
    ifopt_stopid_digits = 5
    train_station_suffixes = {
        ' S ': ' ',
        ' Bf ': ' ',
        'Hauptbahnhof': 'Hbf',
        ' Bahnhof': '',
        'Hbf': 'Hbf',
    }


_names = {
    'vrr': VRR,
}
supported = tuple(_names)


def network(name):
    global supported, _names
    if name not in supported:
        raise NameError('Unsupported network: %s' % name)
    return _names[name]
