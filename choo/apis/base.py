#!/usr/bin/env python3
from ..models import Searchable
from ..models import Trip, Ride, Line, Platform, Location
from weakref import WeakValueDictionary


class API():
    name = None

    def query(self, obj, get_ids=False):
        if not isinstance(obj, (Searchable, Searchable.Request)):
            raise TypeError('can only query Searchable or Searchable.Request')

        if isinstance(obj, Searchable.Request):
            if obj.Model == Trip:
                result, now = self.search_trip(obj)
            elif obj.Model == Ride:
                result, now = self.search_ride(obj)
            elif obj.Model == Line:
                result, now = self.search_line(obj)
            elif obj.Model == Platform:
                result, now = self.search_platform(obj)
            elif obj.Model == Location:
                result, now = self.search_location(obj)
            else:
                raise NotImplementedError()
        else:
            if isinstance(obj, Trip):
                result, now = self.get_trip(obj)
            elif isinstance(obj, Ride):
                result, now = self.get_ride(obj)
            elif isinstance(obj, Line):
                result, now = self.get_line(obj)
            elif isinstance(obj, Platform):
                result, now = self.get_platform(obj)
            elif isinstance(obj, Location):
                result, now = self.get_location(obj)
            else:
                raise NotImplementedError()

        collect = WeakValueDictionary({})
        newresult = result.apply_recursive(time=now, source=self.name, collect=collect)

        for key, value in collect.items():
            if key[0] == 'Stop':
                self._finalize_stop(value)

        return result if newresult is None else newresult

    def search_trip(self, obj):
        assert isinstance(obj, Trip.Request)
        return self._search_trips(obj)

    def search_ride(self, obj):
        assert isinstance(obj, Ride.Request)
        return self._search_rides(obj)

    def search_line(self, obj):
        assert isinstance(obj, Line.Request)
        return self._search_lines(obj)

    def search_platform(self, obj):
        assert isinstance(obj, Platform.Request)
        return self._search_platforms(obj)

    def search_location(self, obj):
        assert isinstance(obj, Location.Request)
        return self._search_locations(obj)

    def get_trip(self, obj):
        assert isinstance(obj, Trip)
        return self._get_trip(obj)

    def get_ride(self, obj):
        assert isinstance(obj, Ride)
        return self._get_ride(obj)

    def get_line(self, obj):
        assert isinstance(obj, Line)
        return self._get_line(obj)

    def get_platform(self, obj):
        assert isinstance(obj, Platform)
        return self._get_platform(obj)

    def get_location(self, obj):
        assert isinstance(obj, Location)
        return self._get_location(obj)

    def _search_trips(self, obj):
        raise NotImplementedError()

    def _search_rides(self, obj):
        raise NotImplementedError()

    def _search_lines(self, obj):
        raise NotImplementedError()

    def _search_platforms(self, obj):
        raise NotImplementedError()

    def _search_locations(self, obj):
        raise NotImplementedError()

    def _get_trip(self, obj):
        raise NotImplementedError()

    def _get_ride(self, obj):
        raise NotImplementedError()

    def _get_line(self, obj):
        raise NotImplementedError()

    def _get_platform(self, obj):
        raise NotImplementedError()

    def _get_location(self, obj):
        raise NotImplementedError()

    def _finalize_stop(self, stop):
        pass
