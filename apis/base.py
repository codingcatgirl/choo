#!/usr/bin/env python3
from models import Collection


class API():
    name = None

    def __init__(self):
        self.collection = Collection()

    def _my_data(self, obj):
        return obj._ids.get(self.name, None)
