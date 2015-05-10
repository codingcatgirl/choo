#!/usr/bin/env python3
from .base import Serializable


class TicketList(Serializable):
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
            # 'other': ((Ticket, ), )
        }

    def _serialize(self, depth):
        data = {}
        data['currency'] = self.currency
        self._serial_add(data, 'level_name')
        data['single'] = self.single.serialize()
        if self.bike:
            data['bike'] = self.bike.serialize()
        data['other'] = {name: t.serialize() for name, t in self.other.items()}
        return data

    def _unserialize(self, data):
        self.currency = data['currency']
        self._serial_get(data, 'level_name')
        self.single = TicketData.unserialize(data['single'])
        if 'bike' in data:
            self.bike = TicketData.unserialize(data['bike'])
        if 'other' in data:
            self.other = {name: TicketData.unserialize(t) for name, t in data['other'].items()}


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

    def _serialize(self, depth):
        data = {}
        data['price'] = self.price
        self._serial_add(data, 'authority')
        self._serial_add(data, 'level')
        if self.price_child:
            data['price_child'] = self.price_child
        return data

    def _unserialize(self, data):
        self.name = data['name']
        self.price = data['price']
        self._serial_get(data, 'authority')
        self._serial_get(data, 'level')
        if 'price_child' in data:
            self.price_child = data['price_child']
