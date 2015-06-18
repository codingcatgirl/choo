Model Reference
===============

transit is composed using a lot of models.

Base Models
-----------

.. py:class:: Serializable

    All models are Serializables.

    .. method:: validate()

        Checks if all attributes have valid values. Raises an exception if the object is not valid. This method is also called by ``serialize()``.

    .. method:: serialize()

        Serializes the object in a JSON-encodable format.

    .. classmethod:: unserialize(data)

        Unserializes any kind of object from a JSON-encodable format.

        :param data: A serialized representation of a transit object
        :rtype: the unserialized object

.. _`Model Serialization`: serializing.html


.. py:class:: Updateable(Serializable)

    An object that can be updated. It has information that can be incomplete or outdated.

    .. py:attribute:: last_update

        The last update or creation date of this object as ``datetime``. Can also be ``None``.

    .. py:attribute:: low_quality

        ``True`` if this event has low quality (otherwise ``None`` or ``False``). This means that this data could be not completely correct (e.g. rarely updated realtime data for train companies that have their own better API) and should be confirmed by explicitly asking an API for it.

    .. method:: update(obj)

        Updates the instance with data from another instance. There are no checks performed whether the other object does indeed describe the same thing.


.. py:class:: Searchable(Updateable)

    An object that can be searched for. You can pass it to the API and to get its complete information.

    All subclasses have a ``Request`` and a ``Results`` subclass. You can pass the and instance of the Request subclass to the API to get search results in a Results subclass.

    .. py:class:: Searchable.Request(Serializable)

        A request template for this Model with lots of possible search criteria that can be set.

    .. py:class:: Searchable.Results(Serializable)

        A list (of Request-Results) of instances of this object. Those lists can have matchscores.

        You can just iterate over this object to get its contents.

        .. method:: scored(obj)

            Returns an iterator over tuples of (results, score).

        .. method:: filter(request)

            Remove all objects that do not match the given Request.

        .. method:: filtered(request)

            Returns a new ``Results`` instance with all objects that do not match the given Request removed.


.. py:class:: Collectable(Searchable)

    An object that can be collected. It has an ID, is unique and is not some kind of data construct.

    .. py:attribute:: _ids

        IDs of this object in different APIs as a dictionary.

        * ``ifopt`` means *Identification of Fixed Objects in Public Transport* which is a gloablly unique ID supported by some APIs.
        * ``uic`` means the international tran station ID of the **International Union of Railways*


Main Models
-----------


.. py:class:: Location(country=None, city=None, name=None, coords=None)

    Base class for Locations. Use this if you want to specify a location using coordinates or if you are not sure what kind of location you are looking for.

    .. attribute:: country

        The country of this location as a two-letter country code.

    .. attribute:: city

        The city this location is located in.

    .. attribute:: name

        The name of this location.

    .. attribute:: coords

        The coordinates of this location as a (lat, lon) float tuple.


.. py:class:: Stop(country=None, city=None, name=None, coords=None)

    A :py:class:`Location` describing a stop, for example: Düsseldorf Hbf.

    .. attribute:: lines

        lines that are available at this stop as an list of :py:class:`Line` objects.

    .. attribute:: rides

        The next rides departing from this stop as an list of :py:class:`RideSegment` starting at this stop.


.. py:class:: Address(country=None, city=None, name=None, coords=None)

    A :py:class:`Location` describing an address.


.. py:class:: POI(country=None, city=None, name=None, coords=None)

    A :py:class:`Location` describing a Point of Interest.


.. py:class:: RealtimeTime(time, delay=None, livetime=None)

    A point in time with optional real time data.

    :param time: The originally planned time as a `datetime.datetime` object.
    :param delay: The (expected) delay as a `datetime.timedelta` object.
    :param livetime: The (expected) actual time as a `datetime.datetime` object.

    You will get an `AssertionError` if you specify both delay and time and they are contradicting each other.

    .. attribute:: time

        The originally planned time as a `datetime.datetime` object.

    .. attribute:: delay

        The (expected) delay as a `datetime.timedelta` object or None.
        Please note that a zero delay is not the same as None. None stands for absence of real time information.

    **The following attributes are dynamic and cannot be set:**

    .. attribute:: is_live

        True if there is real time data available. Shortcut for ``delay is not None``

    .. attribute:: livetime

        The (expected) actual time as a `datetime.datetime` object if real time data is available, otherwise the originally planned time.


.. py:class:: TimeAndPlace(stop: Stop=None, platform: str=None, arrival: RealtimeTime=None, departure: RealtimeTime=None, coords: tuple=None)

    Time and place of a :py:class:`Ride` stopping at a :py:class:`Stop`.

    .. attribute:: stop

        The :py:class:`Stop`.

    .. attribute:: platform

        The platform at which the :py:class:`Ride` can be found at the given time as a string (platforms are not always numeric).

        Please note that different platforms with the same number may exist, depending of the line type (bus, train, …).

    .. attribute:: arrival

        The arrival time of the :py:class:`Ride` as :py:class:`RealtimeTime`.

    .. attribute:: departure

        The departure time of the :py:class:`Ride` as :py:class:`RealtimeTime`.

    .. attribute:: coords

        The coordinates where the train can be found at the given time as a (lat, lon) float tuple.

        This does not mean the coordinates of the Stop. This is not guaranteed to be always the same for the same platform.


.. py:class:: LineTypes(all_types: bool=True)

    A selection of :py:class:`Line` types. Currently, the following line types are supported: 'localtrain', 'longdistance', 'highspeed', 'urban', 'metro', 'tram', 'citybus', 'regionalbus', 'expressbus', 'suspended', 'ship', 'dialable', 'others', 'walk'

    Additionally, the following shortcuts are supported for selecting or unselecting several types at once: 'bus', 'dial'

    :param all_types: whether to select all types initially.

    `in` is supported.

    .. method:: add(*args)

        Add types to the selection.

        :param args: one or more of the supported types

    .. method:: remove(*args)

        Remove types from the selection.

        :param args: one or more of the supported types


.. py:class:: LineType(name: str)

    A :py:class:`Line` type. See :py:class:`LineTypes` for a list of supported line types.

    :param name: the line type

    Comparing to other :py:class:`LineType` objects or strings (including shortcuts) is supported. You will get an exception if you try to compare a :py:class:`LineType` to a string that is not a supported line type or line type shortcut.


.. py:class:: Line(linetype: LineType=None)

    A recurring :py:class:`Ride` with a name/line number. A Line does not have times, only a :py:class:`Ride` does.

    .. attribute:: linetype

        The :py:class:`LineType` of this :py:class:`Line`.

    .. attribute:: product

        The product name, for example `InterCity`, `Hamburg-Köln-Express` or `Niederflurbus`.

    .. attribute:: name

        The long name of the :py:class:`Line`, for example `Rhein-Haardt-Express RE2`.

    .. attribute:: shortname

        The short name of the :py:class:`Line`, for example `RE2`.

    .. attribute:: route

        The route description as a string.

    .. attribute:: first_stop

        The first :py:class:`Stop` of this :py:class:`Line`. Rides may start at a later station.

    .. attribute:: last_stop

        The last :py:class:`Stop` of this :py:class:`Line`. Rides may end at a earlier station.

    .. attribute:: network

        The network this line is part of as a string.

    .. attribute:: operator

        The company that operates this line as a string.


.. py:class:: Ride(line: Line=None, number: str=None)

    A ride is implemented as a list of :py:class:`TimeAndPlace` objects.

    Although a :py:class:`Ride` is iterable, most of the time not all stops of the rides are known and the list of known stations can change. This makes the use of integer indices impossible. To avoid this problem, dynamic indices are used for a :py:class:`Ride`.

    If you iterate over a :py:class:`Ride` each item you get is ``None`` or a :py:class:`TimeAndPlace` object. Each item that is ``None`` stands for n missing stations. It can also mean that the :py:class:`TimeAndPlace` before and after the item are in fact the same. To get rid of all ``None`` items, ask a network API to complete the list of stations of this :py:class:`Ride`.

    You can use integer indices to get, set or delete single :py:class:`TimeAndPlace` objects which is usefull if you want the first (0) or last (-1). But, as explained above, these integer indices may point to another item when the :py:class:`Ride` changes or becomes more complete.

    If you iterate over ``ride.items()`` you get ``(RideStopPointer, TimeAndPlace)`` tuples. When used as an indice, a :py:class:`RideStopPointer` used as an indice will always point to the same :py:class:`TimeAndPlace` object.

    You can slice a :py:class:`Ride` (using integer indices or :py:class RideStopPointer`) which will get you a :py:class:`RideSegment` that will always have the correct boundaries. Slicing with no start or no end point is also supported.

    .. attribute:: line

        The :py:class:`Line` of this :py:class:`Ride`.

    .. attribute:: number

        The number (train number or similar) of this :py:class:`Ride` as a string.

    .. attribute:: bike_friendly

        ``True`` if this is a bike-friendly vehicle, otherwise ``False``.

    .. method:: items()

        A ``(RideStopPointer, TimeAndPlace)`` iterator as explained above.

    .. method:: append(item)

        Append a :py:class:`TimeAndPlace` object.

    .. method:: prepend(item)

        Prepend a :py:class:`TimeAndPlace` object.

    .. method:: insert(position, item)

        Insert a :py:class:`TimeAndPlace` as the new position ``position``.

    **The following attributes are dynamic and cannot be set:**

    .. attribute:: is_complete

        ``True`` if the :py:class:`TimeAndPlace` list is complete and there are no Nones in the list, otherwise ``False``.


.. py:class:: RideStopPointer(i: int)

    *Do not use this class directly.* See :py:class:`Ride` for more information. You can cast a :py:class:`RideStopPointer` as ``int``.


.. py:class:: RideSegment(ride: Ride, origin: RideStopPointer=None, destination: RideStopPointer=None)

    This class created by slicing :py:class:`Ride` objects.

    Integer indices are not too useful in this class, either, although you can for example still use 0 and -1 to get the first or last :py:class:`RideStopPointer` of this segment.

    This model is usable in the same way as a :py:class:`Ride`. Slicing will return another :py:class:`RideSegment`.

    .. attribute:: ride

        The :py:class:`Ride` that this object is a segment of.

    .. method:: items()

        A ``(RideStopPointer, TimeAndPlace)`` iterator over this segment.

    All attributes of the :py:class:`Ride` are also directly accessible through a :py:class:`RideSegment`.

    **This following attributes are dynamic and cannot be set:**

    .. attribute:: is_complete

        ``True`` if the :py:class:`TimeAndPlace` list of this Segment is complete.

    .. attribute:: origin

        The first :py:class:`Stop` of this segment. Shortcut for ``segment[0].stop``.

    .. attribute:: destination

        The last :py:class:`Stop` of this segment. Shortcut for ``segment[-1].stop``.

    .. attribute:: departure

        The departure at the first :py:class:`Stop` of this segment as :py:class:`RealtimeTime`. Shortcut for ``segment[0].departure``.

    .. attribute:: arrival

        The arrival at the last :py:class:`Stop` of this segment as :py:class:`RealtimeTime`. Shortcut for ``segment[-1].arrival``.


.. py:class:: Way(origin: Location, destination: Location, distance: int=None)

    Individual transport (walk, bike, taxi…) with no schedule. Used for example to get from a :py:class:`Location` that is not a :py:class:`Stop` to a :py:class:`Stop` and for changes but also for trips that are faster by foot.

    .. attribute:: origin

        The start point :py:class:`Location`.

    .. attribute:: destination

        The end point :py:class:`Location`.

    .. attribute:: distance

        The distance in meters as ``int``.

    .. attribute:: duration

        The expected duration as ``datetime.timedelta``.

    .. attribute:: path

        The path as a list of coordinates as (lat, lon) tuples.


.. py:class:: Trip()

    A connection from a :py:class:`Location` to another :py:class:`Location`.

    .. attribute:: parts

        A iterable of :py:class:`RideSegment` and :py:class:`Way` objects.

    .. attribute:: walk_speed

        Walk speed assumed for this trip as a string. (``slow``, ``normal`` or ``fast``)

    **The following attributes are dynamic** and can not be overwritten – their values are taken from ``parts`` when you access them:

    .. attribute:: origin

        The start :py:class:`Location` of this trip.

    .. attribute:: destination

        The end :py:class:`Location` of this trip.

    .. attribute:: departure

        The departure at the first :py:class:`Location` of this trip as :py:class:`RealtimeTime`. (If there are leading :py:class:`Way` objects they need to have the ``duration`` attribute set in order for this to work)

    .. attribute:: arrival

        The arrival at the last :py:class:`Location` of this trip as :py:class:`RealtimeTime`. (If there are trailing :py:class:`Way` objects they need to have the ``duration`` attribute set in order for this to work)

    .. attribute:: linetypes

        The line types that occur in this trip as :py:class:`LineTypes`.

    .. attribute:: changes

        The number of changes in this trip.

    .. attribute:: bike_friendly

        ``False`` if at least one :py:class:`Ride` that is part of this trip is not bike friendly. ``True`` if all of them are. ``None`` if there is no bike friendly information for all rides but those that have the information are bike friendly.


.. py:class:: TripRequest()

    A description of a trip used to search for Trips.

    .. attribute:: origin

        The start :py:class:`Location` of the trip.

    .. attribute:: destination

        The end :py:class:`Location` of the trip.

    .. attribute:: departure

        The minimum departure time as :py:class:`RealtimeTime` or ``datetime.datetime``.

        If both times are ``None`` the behaviour is as if you would have set the departure time to the current time right before sending the request.

    .. attribute:: arrival

        The latest allowed arrival as :py:class:`RealtimeTime` or ``datetime.datetime``.

    .. attribute:: linetypes

        The line types that are allowed as :py:class:`LineTypes`.

    .. attribute:: max_changes

        The maximum number of changes allowed.

    .. attribute:: bike_friendly

        Set this to ``True`` if the route has to be bike friendly.
