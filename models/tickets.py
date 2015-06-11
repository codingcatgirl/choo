#!/usr/bin/env python3
from .base import Updateable, Serializable


class TicketList(Updateable):
    def __init__(self):
        self.currency = None
        self.level_name = None
        self.single = None
        self.bike = None
        self.other = {}

    @classmethod
    def _validate(cls):
        return {
            'currency': str,
            'level_name': (None, str),
            'single': TicketData,
            'bike': (None, TicketData),
            'other': None
        }

    def _validate_custom(self, name, value):
        if name == 'other':
            if not isinstance(value, dict):
                return False
            for k, v in value.items():
                if not isinstance(k, str) or not isinstance(v, TicketData):
                    return False
            return True

    def _serialize_custom(self, name):
        if name == 'other':
            return 'other', {name: t.serialize() for name, t in self.other.items()}

    def _unserialize_custom(self, name, data):
        if name == 'other':
            self.other = {name: TicketData.unserialize(t) for name, t in data.items()}

    def __repr__(self):
        return '<TicketList %s %s (+%d)>' % (self.currency, repr(self.single), len(self.other))


class TicketData(Serializable):
    def __init__(self, authority=None, level=None, price=None, price_child=None):
        self.authority = authority
        self.level = level
        self.price = price
        self.price_child = price_child

    @classmethod
    def _validate(cls):
        return {
            'authority': (str, None),
            'level': (str, None),
            'price': float,
            'price_child': (None, float),
        }

    def __repr__(self):
        childprice = ''
        if self.price_child is not None:
            childprice = ' %.2f' % self.price_child
        return '<TicketData %s %s %.2f%s>' % (self.authority, self.level, self.price, childprice)
