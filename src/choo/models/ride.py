#!/usr/bin/env python3
from .base import Serializable, Collectable, TripPart
from .locations import Coordinates
from .ridepoint import RidePoint
from .line import Line
from . import fields
import math


class RideIterable(Serializable):
    def __init__(self, **kwargs):
        if self.__class__ == RideIterable:
            raise RuntimeError('Only instances of RideIterable subclasses are allowed!')
        super().__init__(**kwargs)

    def __len__(self):
        i = 0
        for elem in self._elems():
            i += 1
        return i

    def _get_elem(self, key, silent=False):
        if key is None:
            return None
        if key < 0:
            elem = self._last
            for i in range(1+key):
                if elem is self._first:
                    raise IndexError('%s index out of range' % self.__class__.__name__)
                elem = elem.prev
            return elem

        elem = self._first
        for i in range(key):
            if elem is self._last:
                raise IndexError('%s index out of range' % self.__class__.__name__)
            elem = elem.next
        return elem

    def __getitem__(self, key):
        if not isinstance(key, (int, slice)):
            raise TypeError('%s indices must be integers, not %s' % (self.__class__.__name__, type(key).__name__))

        if isinstance(key, slice):
            if key.step is not None:
                raise TypeError('%s cannot be sliced with steps', self.__class__.__name__)
            if not ((key.start is None or isinstance(key.start, (int, Ride.Element))) and
                    (key.stop is None or isinstance(key.stop, (int, Ride.Element)))):
                raise TypeError('slice indices must be integers or None')

            return RideSegment(self, self._get_elem(key.start) if isinstance(key.start, int) else key.start,
                               self._get_elem(key.stop) if isinstance(key.stop, int) else key.stop)

        return self._get_elem(key).point

    def __iter__(self):
        for elem in self._elems():
            yield elem.point

    def _elems(self):
        elem = self._first
        while True:
            yield elem
            if elem == self._last:
                break
            elem = elem.next

    def index(self, item):
        if item is not None and not isinstance(item, RidePoint):
            raise TypeError('%s elements must be RidePoints, not %s' % (self.__class__.__name__, type(item).__name__))

        for i, point in enumerate(self):
            if point == item:
                return i
        raise ValueError('%s is not in %s' % (repr(item), self.__class__.__name__))

    def _elem_index(self, item):
        assert isinstance(item, Ride.Element)

        for i, elem in enumerate(self._elems()):
            if elem is item:
                return i
        raise ValueError('%s is not in %s' % (repr(item), self.__class__.__name__))

    def __contains__(self, item):
        try:
            self.index(item)
        except(ValueError):
            return False
        return True

    def _distance_in_meters(self, c1, c2):
        deg2rad = math.pi/180.0

        phi1 = (90.0 - c1.lat)*deg2rad
        phi2 = (90.0 - c2.lat)*deg2rad

        return math.acos((math.sin(phi1)*math.sin(phi2)*math.cos(c1.lon*deg2rad - c2.lon*deg2rad) +
                          math.cos(phi1)*math.cos(phi2)))*6378100

    def set_path(self, path):
        elems = tuple(self._elems())
        points = [(e.point.platform if e.point is not None else None) for e in elems]

        # Remove leading and trailing unidentified points
        enum_points = tuple(enumerate(points))
        for i, point in enum_points:
            if point is None or point.lat is not None and point.lon is not None:
                first = i
                break
        else:
            # No positioned points
            return
        for i, point in reversed(enum_points):
            if point is None or point.lat is not None and point.lon is not None:
                last = i
                break
        elems = elems[first:last+1]
        points = points[first:last+1]

        if None in points:
            # todo: Has to be uninterrupted point sequence for now
            return

        # Init
        indexes = [None] * len(points)
        distances = [float('Inf')] * len(points)

        # Find Points that are too close to not be right
        for i, coord in enumerate(path):
            for j, point in enumerate(points):
                d = self._distance_in_meters(point, coord)
                if 15 > d < distances[j]:
                    indexes[j] = i
                    distances[j] = d

        # For the rest, find a place between to points
        lastcoord = None
        for i, coord in enumerate(path):
            if not (None is not lastcoord != coord):
                continue

            for j, point in enumerate(points):
                if indexes[j] is not None:
                    continue

                # print([coord.serialize(), point.serialize(), lastcoord.serialize()])
                if 2.84 < abs(math.atan2(coord.lat - point.lat, coord.lon - point.lon) -
                              math.atan2(lastcoord.lat - point.lat, lastcoord.lon - point.lon)) < 3.44:
                    indexes[j] = i
                    distances[j] = 0
                    break

        # if still some points are not found on the line, just take the closest
        for i, coord in enumerate(path):
            for j, point in enumerate(points):
                d = self._distance_in_meters(point, coord)
                if 100 > d < distances[j]:
                    indexes[j] = i
                    distances[j] = d

        # No points found
        if not [i for i in indexes if i is not None]:
            return

        # Remove leading and trailing unidentified points
        first = 0
        last = len(points)-1
        while first < last and indexes[first] is None:
            first += 1
        while first < last and indexes[last] is None:
            last -= 1
        elems = elems[first:last]
        indexes = indexes[first:last+1]

        # We have to have identified each point between the bounds
        if None in indexes:
            return

        # If we found the points in the wrong order, we failed
        if sorted(indexes) != indexes:
            return

        for i, elem in enumerate(elems):
            elem.path_to_next = path[indexes[i]:indexes[i+1]]

    @property
    def path(self):
        path = []
        for elem in self._elems():
            p = elem.point
            if p is None:
                continue
            c = p.to_coordinates()
            if c is not None:
                path.append(c)
            if elem != self._last:
                path.extend(elem.path_to_next)
        return path


class MetaRide(Collectable):
    line = fields.Model(Line, none=False)
    number = fields.Field(str)
    direction = fields.Field(str)
    bike_friendly = fields.Field(bool)
    annotation = fields.List(str)

    def __init__(self, **kwargs):
        # magic, do not remove
        super().__init__(**kwargs)


class Ride(Collectable, RideIterable):
    meta = fields.Model(MetaRide, none=False)
    time = fields.DateTime()
    canceled = fields.Field(bool)
    infotexts = fields.List(str)

    def __init__(self, line=None, number=None, **kwargs):
        self._first = self._last = None
        super().__init__(line=line, number=number, **kwargs)

    def validate(self):
        for point in self:
            if point is None:
                continue
            # todo: point.validate()
        return super().validate()

    def serialize(self, **kwargs):
        data = super().serialize(**kwargs)
        data['points'] = [e.serialize(**kwargs) for e in self._elems()]
        return data

    @classmethod
    def unserialize(cls, data, part_of_segment=False):
        if not part_of_segment and ('@origin' in data or '@destination' in data):
            return RideSegment.unserialize(data)

        self = super(Ride, cls).unserialize(data)

        for e in data.get('points', []):
            elem = Ride.Element.unserialize(e) if e is not None else Ride.Element(None)
            elem.prev = self._last
            if self._first is None:
                self._first = elem
            if self._last is not None:
                self._last.next = elem
            self._last = elem

        return self

    def apply_recursive(self, **kwargs):
        if 'time' in kwargs:
            self.time = kwargs['time']

        for elem in self._elems():
            if elem.point is None:
                continue
            newpoint = elem.point.apply_recursive(**kwargs)
            if newpoint is not None:
                elem.point = newpoint

        return super().apply_recursive(**kwargs)

    def __setitem__(self, key, item):
        if not isinstance(key, int):
            raise TypeError('Ride indices must be integers, not %s' % type(key).__name__)
        if item is not None and not isinstance(item, RidePoint):
            raise TypeError('Ride elements must be RidePoints or None, not %s' % type(item).__name__)

        self._get_elem(key).point = item

    def __delitem__(self, key):
        self.pop(key)

    def append(self, item):
        if item is not None and not isinstance(item, RidePoint):
            raise TypeError('Ride elements must be RidePoints or None, not %s' % type(item).__name__)

        elem = Ride.Element(item, prev=self._last)

        if self._first is None:
            self._first = self._last = elem
            return

        if self[-1] is item is None:
            return

        self._last.next = elem
        self._last = elem

    def prepend(self, item):
        if item is not None and not isinstance(item, RidePoint):
            raise TypeError('Ride elements must be RidePoints or None, not %s' % type(item).__name__)

        elem = Ride.Element(item, next_=self._first)

        if self._first is None:
            self._first = self._last = elem
            return

        if self[0] is item is None:
            return

        self._first.prev = elem
        self._first = elem

    def insert(self, position, item):
        if not isinstance(position, int):
            raise TypeError('Ride indices must be integers, not %s' % type(position).__name__)
        if item is not None and not isinstance(item, RidePoint):
            raise TypeError('Ride elements must be RidePoints or None, not %s' % type(item).__name__)

        try:
            elem = self._get_elem(position)
        except(IndexError):
            if position == len(self):
                return self.append(item)
            else:
                raise

        if elem == self._first:
            return self.prepend(item)

        # Insert element and reevaluate path
        segment = self[elem.prev:elem.next]
        path = segment.path
        newelem = Ride.Element(item, prev=elem.prev, next_=elem)
        elem.prev.path_to_next = []
        elem.prev.next = newelem
        elem.prev = newelem
        segment.set_path(path)

    def _remove_elem(self, elem):
        if elem != self._first:
            elem.prev.next = elem.next
        else:
            self._first = elem.next
        if elem != self._last:
            elem.next.prev = elem.prev
        else:
            self._last = elem.prev

        # this usually means that the ride has been reroutet, so delete path
        if elem != self._first:
            elem.prev.path_to_next = []

        if elem.prev is not None and elem.next is not None and elem.prev.pointer is elem.next.pointer is None:
            self._remove_elem(elem.next)

        elem.next = elem.prev = None

    def remove(self, item):
        if item is None:
            raise TypeError('Ride.remove(x): can not remove all Nones')

        if not isinstance(item, RidePoint):
            raise TypeError('Ride elements must be RidePoints or None, not %s' % type(item).__name__)

        for elem in self._elems():
            if elem.point == item:
                self._remove_elem(elem)
                return

        raise ValueError('Ride.remove(x): x not in Ride')

    def pop(self, key=-1):
        if not isinstance(key, int):
            raise TypeError('Ride indices must be integers, not %s' % type(key).__name__)

        elem = self._get_elem(key)
        self._remove_elem(elem)
        return elem.point

    def __eq__(self, other):
        if not isinstance(other, Ride):
            return False

        by_id = self._same_by_id(other)
        if by_id is not None:
            return by_id

        if self.line is not None and other.line is not None and self.line != other.line:
            return False

        if self.number is not None and other.number is not None and self.number != other.number:
            return False

        if self[-1] is not None and other[-1] is not None and self[-1].stop != other[-1].stop:
            return False

        if self[0] is not None and other[0] is not None and self[0].stop != other[0].stop:
            return False

        for point in self:
            if point is None:
                continue
            for point2 in self:
                if point2 is None:
                    continue
                if point == point2:
                    return True

        return None

    def __getattr__(self, name):
        return getattr(self.meta, name)

    def __repr__(self):
        return '<Ride %s %s>' % (self.meta.number, repr(self.meta.line))

    class Element(Serializable):
        def __init__(self, point, prev=None, next_=None):
            self.point = point
            self.prev = prev
            self.next = next_
            self.path_to_next = []

        def serialize(self, **kwargs):
            if self.point is None:
                return None
            data = super().serialize(**kwargs)
            data = self.point.serialize(**kwargs)
            if self.path_to_next:
                data['path_to_next'] = [tuple(c) for c in self.path_to_next]
            return data

        @classmethod
        def unserialize(cls, data):
            self = Ride.Element(RidePoint.unserialize(data) if data is not None else None)
            self.path_to_next = [Coordinates.unserialize(c) for c in data.get('path_to_next', [])]
            return self


class RideSegment(TripPart, RideIterable):
    ride = fields.Model(Ride, none=False)

    def __init__(self, ride=None, origin=None, destination=None, **kwargs):
        super().__init__(**kwargs)

        self.ride = ride
        self._origin = origin
        self._destination = destination
        elem = self._first
        while True:
            if elem == self._last:
                break
            elem = elem.next
        else:
            raise ValueError('Impossible RideSegment')

    @property
    def _first(self):
        return self.ride._first if self._origin is None else self._origin

    @property
    def _last(self):
        return self.ride._last if self._destination is None else self._destination

    def validate(self):
        assert self._origin is None or isinstance(self._origin, Ride.Element)
        assert self._destination is None or isinstance(self._destination, Ride.Element)
        return super().validate()

    def serialize(self, **kwargs):
        data = super().serialize(**kwargs)
        if self._origin is not None:
            data['@origin'] = self.ride._elem_index(self._origin)

        if self._destination is not None:
            data['@destination'] = self.ride._elem_index(self._destination)
        data.update(data['ride'])
        del data['ride']
        return data

    @classmethod
    def unserialize(cls, data):
        assert data.get('type', 'Ride') == 'Ride'
        self = cls(Ride.unserialize(data, True))

        origin = data.get('@origin')
        if origin is not None:
            self._origin = self.ride._get_elem(origin)

        destination = data.get('@destination')
        if destination is not None:
            self._destination = self.ride._get_elem(destination)

        return self

    @property
    def origin(self):
        return self[0].stop

    @property
    def destination(self):
        return self[-1].stop

    @property
    def departure(self):
        return self[0].departure

    @property
    def arrival(self):
        return self[-1].arrival

    def __getattr__(self, name):
        return getattr(self.ride, name)

    def __eq__(self, other):
        if not isinstance(other, RideSegment):
            return False

        if self.ride is other.ride:
            return self._origin == other._origin and self._destination == other._destination
        elif self.ride == other.ride:
            return (self.origin == other.origin and self.departure == other.departure and
                    self.destination == other.destination and self.arrival == other.arrival)
        return False

    def __repr__(self):
        return '<RideSegment %s %s %s>' % (repr(self.origin), repr(self.destination), repr(self.ride))