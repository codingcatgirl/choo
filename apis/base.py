#!/usr/bin/env python3
from models.base import ModelBase


class API():
    name = None

    def _my_data(self, obj: ModelBase):
        return obj._ids.get(self.name, None)
