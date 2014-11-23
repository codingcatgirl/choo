#!/usr/bin/env python3
from models import ModelBase


class API():
    name = None

    def _my_data(self, obj: ModelBase):
        return obj.ids.get(self.name, None), obj.raws.get(self.name, None)
