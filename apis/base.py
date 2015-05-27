#!/usr/bin/env python3


class API():
    name = None

    def _my_data(self, obj):
        return obj._ids.get(self.name, None)
