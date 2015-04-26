#!/usr/bin/env python3
from .base import ModelBase, Serializable


class Coordinates(Serializable):
    _validate = {
        'lat': float,
        'lon': float
    }
    
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        
    def _serialize(self, depth):
        return [self.lat, self.lon]
        
    def _unserialize(self, data):
        self.lat, self.lon = data
        

class Location(ModelBase):
    _validate = {
        'country': (None, str),
        'city': (None, str),
        'name': str,
        'coords': (None, Coordinates)
    }
    
    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        self.country = country
        self.city = city
        self.name = name
        self.coords = coords

    def _serialize(self, depth):
        data = {}
        self._serial_add(data, 'country')
        self._serial_add(data, 'city')
        self._serial_add(data, 'name')
        if self.coords:
            data['coords'] = self.coords.serialize()
        return data
        
    def _unserialize(self, data):
        self._serial_get(data, 'country')
        self._serial_get(data, 'city')
        self._serial_get(data, 'name')
        if 'coords' in data:
            self.coords = Coordinates.unserialize(data['coords'])
            
            
class POI(Location):
    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)


class Address(Location):
    def __init__(self, country=None, city=None, name=None, coords=None):
        super().__init__()
        Location.__init__(self, country, city, name, coords)
            
        
class Way(ModelBase):
    def __init__(self, origin: Location, destination: Location, distance: int=None):
        super().__init__()
        self.origin = origin
        self.destination = destination
        self.distance = None
        self.duration = None
        self.path = None
        # todo: self.stairs = None

    @classmethod
    def load(cls, data):
        origin = Location.unserialize(data['origin'])
        destination = Location.unserialize(data['destination'])
        obj = cls(origin, destination)
        obj.distance = data.get('distance', None)
        obj.duration = data.get('duration', None)
        obj.path = data.get('path', None)
        if obj.path:
            obj.path = [self.unserialize(p) for p in obj.path]
        return obj

    def __eq__(self, other):
        return (isinstance(other, Way) and self.origin == other.origin and self.destination == other.destination)

    def _serialize(self, ids):
        data = {}
        self._serial_add(data, 'origin', ids)
        self._serial_add(data, 'destination', ids)
        self._serial_add(data, 'distance', ids)
        self._serial_add(data, 'duration', ids)
        if self.path:
            path = [('tuple', v) for v in self.path]
            self._serial_add(data, 'path', ids, val=path)
        return data