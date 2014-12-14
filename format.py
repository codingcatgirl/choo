#!/usr/bin/env python3
from apis.efa import EFA


class VRR(EFA):
    name = 'vrr'
    base_url = 'http://app.vrr.de/standard/'
    country = 'de'

    def __init__(self):
        self.ids = {}
        self.raws = {}
