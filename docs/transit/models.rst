Model Reference
===============

Attributes that may be ``None`` are marked with a ⁰-Symbol.

Base Classes
------------

All transit models are based upon one of the following four base classes that build on top of each other.


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


.. py:class:: Updateable

    A :py:class:`Serializable` that can be updated. It has information that can be incomplete or outdated.

    .. py:attribute:: last_update⁰

        The last update or creation date of this object as ``datetime``.

    .. py:attribute:: low_quality⁰

        ``True`` if this event has low quality (otherwise ``None`` or ``False``). This means that this data could be not completely correct (e.g. rarely updated realtime data for train companies that have their own better API) and should be confirmed by explicitly asking an API for it.

    .. method:: update(obj)

        Updates the instance with data from another instance. There are no checks performed whether the other object does indeed describe the same thing.


.. py:class:: Searchable

    An :py:class:`Updateable` that can be searched for. You can pass it to the API and to get its complete information.

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


.. py:class:: Collectable

    A :py:class:`Searchable` that can be collected. It has an ID and it really exists and is not some kind of data construct.

    .. py:attribute:: _ids

        IDs of this object in different APIs as a dictionary.

        * ``ifopt`` means *Identification of Fixed Objects in Public Transport* which is a gloablly unique ID supported by some APIs.

        * ``uic`` is the international train station id by the *International Union of Railways*.



Main Models
-----------

Submodels of :py:class:``Collectable``.

.. py:class:: AbstractLocation

    Base class for everything that has a fixed position.

    .. attribute:: coords⁰

        The :py:class:`Coordinates` of this location.

    .. py:class:: AbstractLocation.Request

        Submodel of :py:class:`Searchable.Request`.

    .. py:class:: AbstractLocation.Results

        Submodel of :py:class:`Searchable.Results`.


.. py:class:: Ride(line=None, number=None)

    A ride is implemented as a list of :py:class:`TimeAndPlace` objects.

    Although a :py:class:`Ride` is iterable, most of the time not all stops of the rides are known and the list of known stations can change. This makes the use of integer indices impossible. To avoid this problem, dynamic indices are used for a :py:class:`Ride`.

    If you iterate over a :py:class:`Ride` each item you get is ``None`` or a :py:class:`TimeAndPlace` object. Each item that is ``None`` stands for n missing stations. It can also mean that the :py:class:`TimeAndPlace` before and after the item are in fact the same. To get rid of all ``None`` items, pass an incomplete ride to a network API.

    You can use integer indices to get, set or delete single :py:class:`TimeAndPlace` objects which is usefull if you want the first (0) or last (-1). But, as explained above, these integer indices may point to another item when the :py:class:`Ride` changes or becomes more complete.

    If you iterate over ``ride.items()`` you get ``(RideStopPointer, TimeAndPlace)`` tuples. When used as an indice, a :py:class:`Ride.StopPointer` used as an indice will always point to the same :py:class:`TimeAndPlace` object.

    You can slice a :py:class:`Ride` (using integer indices or :py:class RideStopPointer`) which will get you a :py:class:`RideSegment` that will always have the correct boundaries. Slicing with no start or no end point is also supported.

    .. attribute:: line

        The :py:class:`Line` of this :py:class:`Ride`.

    .. attribute:: number⁰

        The number (train number or similar) of this :py:class:`Ride` as a string.

    .. attribute:: canceled⁰

        A boolean indicating whether this ride has been canceled.

    .. attribute:: bike_friendly⁰

        A boolean indicating whether this is a bike-friendly vehicle.

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

    .. py:class:: Ride.StopPointer

        See above. Immutable. Do not use this class directly. You can cast it to int.

    .. py:class:: Ride.Request

        Submodel of :py:class:`Searchable.Request`.

    .. py:class:: Ride.Results

        Submodel of :py:class:`Searchable.Results`.


.. py:class:: Line(linetype=None)

    A group of Rides (e.g. Bus Line 495). Every :py:class:`Ride` belongs to one Line.

    .. attribute:: linetype

        The :py:class:`LineType` of this :py:class:`Line`.

    .. attribute:: product⁰

        The product name, for example `InterCity`, `Hamburg-Köln-Express` or `Niederflurbus`.

    .. attribute:: name

        The long name of the :py:class:`Line`, for example `Rhein-Haardt-Express RE2`.

    .. attribute:: shortname

        The short name of the :py:class:`Line`, for example `RE2`.

    .. attribute:: route⁰

        The route description.

    .. attribute:: first_stop⁰

        The first :py:class:`Stop` of this :py:class:`Line`. Rides may start at a later station.

    .. attribute:: last_stop⁰

        The last :py:class:`Stop` of this :py:class:`Line`. Rides may end at a earlier station.

    .. attribute:: network⁰

        The name of the network this :py:class:`Line` is part of as a string.

    .. attribute:: operator⁰

        The name of the company that operates this line.

    .. py:class:: Line.Request

        Submodel of :py:class:`Searchable.Request`.

    .. py:class:: Line.Results

        Submodel of :py:class:`Searchable.Results`.



Locations
---------

Submodels of :py:class:`AbstractLocation`.

.. py:class:: Platform(stop, name=None, full_name=None)

    An :py:class:`AbstractLocation` where rides stop (e.g. Gleis 7). It belongs to one :py:class:`Stop`.

    .. attribute:: stop

        The :py:class:`Stop` this platform belongs to.

    .. attribute:: name⁰

        The name of this Platform (e.g. 7 or 2b).

    .. attribute:: full_name⁰

        The full name of this Platform (e.g. Bussteig 7 or Gleis 2b)

    .. py:class:: Platform.Request

        Submodel of :py:class:`AbstractLocation.Request`.

    .. py:class:: Platform.Results

        Submodel of :py:class:`AbstractLocation.Results`.


.. py:class:: Location(country=None, city=None, name=None)

    An :py:class:`AbstractLocation` that is named and not a sublocation like a Platform.

    .. attribute:: country⁰

        The country of this location as a two-letter country code.

    .. attribute:: city⁰

        The name of the city this location is located in.

    .. attribute:: name

        The name of this location. If the ``city`` attribute is ``None`` this it may also included in the name.

    .. attribute:: near_stops⁰

        Other stops near this one as a ``Stop.Results``, if available. You can always search for Stops near an :py:class:`AbstractLocation` directly using ``AbstractLocation.Request``.

    .. py:class:: Location.Request

        Submodel of :py:class:`AbstractLocation.Request`.

    .. py:class:: Location.Results

        Submodel of :py:class:`AbstractLocation.Results`.


.. py:class:: Stop(country=None, city=None, name=None)

    A :py:class:`Location` describing a stop, for example: Düsseldorf Hbf.

    .. attribute:: train_station_name⁰

        The official train station name if this stop belongs to a train station. This is the difference between the Stop **Hauptbahnhof** in **Düsseldorf** and the name of the train station **Düsseldorf Hbf**.

    .. attribute:: lines⁰

         The Lines that are available at this stop as a ``Line.Results`` object, if available. You can always search for Lines at a :py:class:`Stop` using :py:class:`Line.Request`.

    .. attribute:: rides⁰

        The next rides at this stop as a ``Ride.Results`` object, if available. You can always search for Rides at a :py:class:`Stop` using :py:class:`Ride.Request`.

    .. py:class:: Stop.Request

        Submodel of :py:class:`Location.Request`.

    .. py:class:: Stop.Results

        Submodel of :py:class:`Location.Results`.


.. py:class:: Address(country=None, city=None, name=None)

    A :py:class:`Location` describing an address. The ``name`` attribute contains the address in one string, but more detailed attributes may be available:

    .. attribute:: street⁰

        The name of the street.

    .. attribute:: number⁰

        The house number as a string.

    .. py:class:: Address.Request

        Submodel of :py:class:`Location.Request`.

    .. py:class:: Address.Results

        Submodel of :py:class:`Location.Results`.


.. py:class:: POI(country=None, city=None, name=None)

    A :py:class:`Location` describing a Point of Interest.

    .. py:class:: POI.Request

        Submodel of :py:class:`Location.Request`.

    .. py:class:: POI.Results

        Submodel of :py:class:`Location.Results`.



Trips
-----

Submodel of :py:class:`Searchable`.

.. py:class:: Trip()

    A connection from a :py:class:`AbstractLocation` to another :py:class:`AbstractLocation`.

    It consists of a list of :py:class:`RideSegment` and :py:class:`Way` objects. Just iterate over it to get its elements.

    .. attribute:: tickets⁰

        :py:class:`TicketList` of available tickets for this trip.

    **The following attributes are dynamic** and can not be set – their values are taken from ``parts`` when you access them:

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

    .. attribute:: wayonly

        A boolean indicating whether this Trip only consists of :py:class:`Way` objects.

    .. attribute:: changes

        The number of changes in this trip (number of ``RideSegments`` minus one with a minimum of zero)

    .. attribute:: bike_friendly

        ``False`` if at least one :py:class:`Ride` that is part of this trip is not bike friendly. ``True`` if all of them are. ``None`` if there is no bike friendly information for all rides but those that have the information are bike friendly.

    .. py:class:: Trip.Request

        Submodel of :py:class:`Searchable.Request`.

        .. attribute:: origin

            The start :py:class:`AbstractLocation` of the trip.

        .. attribute:: destination

            The end :py:class:`AbstractLocation` of the trip.

        .. attribute:: departure⁰

            The minimum departure time as :py:class:`RealtimeTime` or ``datetime.datetime``.

            If both times are ``None`` the behaviour is as if you would have set the departure time to the current time right before sending the request. (Default: ``None``)

        .. attribute:: arrival⁰

            The latest allowed arrival as :py:class:`RealtimeTime` or ``datetime.datetime``. (Default: ``None``)

        .. attribute:: linetypes

            The line types that are allowed as :py:class:`LineTypes`. (Default: all)

        .. attribute:: max_changes⁰

            The maximum number of changes allowed or ``None`` for no limit. (Default: ``None``)

        .. attribute:: with_bike

            Whether a bike should be taken along. (Default: ``False``)

        .. attribute:: wheelchair

            Whether to allow only vehicles that support wheelchairs. (Default: ``False``)

        .. attribute:: low_floor_only

            Whether to allow only low floor vehicles. (Default: ``False``)

        .. attribute:: allow_solid_stairs

            Whether to allow solid stairs. (Default: ``True``)

        .. attribute:: allow_escalators

            Whether to allow escalators. (Default: ``True``)

        .. attribute:: allow_elevators

            Whether to allow elevators. (Default: ``True``)

        .. attribute:: waytype_origin

            Waytype at the beginning of the trip. (Default: walk)

        .. attribute:: waytype_via

            Waytype at changes or ways during the trip. (Default: walk)

        .. attribute:: waytype_destination

            Waytype at the end of the trip. (Default: walk)

        .. attribute:: wayduration_origin

            Maximum duration of a way at the beginning of the trip as a ``datetime.timedelta``. (Default: 10 minutes)

        .. attribute:: wayduration_via

            Maximum duration of changes of ways during the trip as a ``datetime.timedelta``. (Default: 10 minutes)

        .. attribute:: wayduration_destination

            Maximum duration of a way at the end of the trip as a ``datetime.timedelta``. (Default: 10 minutes)

    .. py:class:: Trip.Results

        Submodel of :py:class:`Searchable.Results`.

        .. attribute:: origin

            The start :py:class:`AbstractLocation` of the trip.

        .. attribute:: destination

            The end :py:class:`AbstractLocation` of the trip.



Trip parts
----------

Submodels of :py:class:`Serializable`.

.. py:class:: RideSegment

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

    Individual transport (walk, bike, taxi…) with no schedule. Used for example to get from a :py:class:`Address` to a :py:class:`Stop` and for changes but also for trips that are faster by foot.

    .. attribute:: origin

        The start point :py:class:`Location`.

    .. attribute:: destination

        The end point :py:class:`Location`.

    .. attribute:: distance

        The distance in meters as ``int``.

    .. attribute:: duration

        The expected duration as ``datetime.timedelta``.

    .. attribute:: path

        The path as a list of :py:class:`Coordinates`.

    .. attribute:: events

        Events on the way (e.g. taking escalators upwards) as a (ordered) list of :py:class:`WayEvent`.



Other Models
------------

Submodels of :py:class:`Updateable`.

.. py:class:: TimeAndPlace(platform, arrival=None, departure=None)

    Time and place of a :py:class:`Ride` stopping at a :py:class:`Platform`.

    .. attribute:: platform

        The :py:class:`Platform`.

    .. attribute:: arrival⁰

        The arrival time of the :py:class:`Ride` as :py:class:`RealtimeTime`.

    .. attribute:: departure⁰

        The departure time of the :py:class:`Ride` as :py:class:`RealtimeTime`.

    .. attribute:: passthrough⁰

        A boolean indicating whether the ride does not actualle stop at this :py:class:`Stop` but pass through it.


.. py:class:: RealtimeTime(time, delay=None)

    A point in time with optional real time data.

    :param time: The originally planned time as a `datetime.datetime` object.
    :param delay: The (expected) delay as a `datetime.timedelta` object if known.

    .. attribute:: time

        The originally planned time as a `datetime.datetime` object.

    .. attribute:: delay⁰

        The (expected) delay as a `datetime.timedelta` object or None.
        Please note that a zero delay is not the same as None. None stands for absence of real time information.

    Note that the ``last_update`` attribute (inherited from :py:class:`Updateable`) tells you how up to date the real time information is.

    **The following attributes are dynamic and cannot be set:**

    .. attribute:: is_live

        True if there is real time data available. Shortcut for ``delay is not None``

    .. attribute:: livetime

        The (expected) actual time as a `datetime.datetime` object if real time data is available, otherwise the originally planned time.


.. py:class:: TicketList(all_types: bool=True)

    A list of tickets.

    .. attribute:: currency

        The name or abbreviation of the currency.

    .. attribute:: level_name⁰

        How a level is named at this network.

    .. attribute:: single

        The single ticket as :py:class:`TicketData`.

    .. attribute:: bike⁰

        The single ticket as :py:class:`TicketData`.

    .. attribute:: other

        Other available tickets as a dictionary with the name of the tickets as keys and :py:class:`TicketData` objects as values.



Data types
-------------------------

Submodels of :py:class:`Serializable`.

.. py:class:: TicketData(authority=None, level=None, price=None, price_child=None)

    Information about a ticket.

    .. attribute:: authority⁰

        The name of the authority selling this ticket.

    .. attribute:: level⁰

        The level of this ticket, e.g. A or something similar, depending on the network

    .. attribute:: price

        The price of this ticket as float.

    .. attribute:: price_child⁰

        The children’s price for this ticket if this ticket is not a ticket for children only but has a different price for children.


.. py:class:: LineType(name)

    Each :py:class:`Line` has a line type. A line type has one of the values ``(empty string)``, ``train``, ``train.local``, ``train.longdistance``, ``train.longdistance.highspeed``,
    ``urban``, ``metro``, ``tram``, ``bus``, ``bus.regional``, ``bus.city``, ``bus.express``, ``suspended``, ``ship``, ``dialable``, or ``other``.

    An empty string means that it can be anyone of the other linetypes, The linetype ``bus`` means that it could be any of the bus-subtypes. The reason for this is that
    not all networks differentiate between some subtyes (e.g. bus types). See the network reference for which linetypes it may output.

    All identical linetypes are the same instance:

    .. code-block:: python

        >>> LineType('bus') is LineType('bus')
        True

    To compare against a linetype, use the ``in`` operator. Be aware that this operator is not transitive!

    .. code-block:: python

        >>> linetype = LineType('bus.express')
        >>> linetype in LineType('bus')
        True
        >>> LineType('bus') in linetype
        False

        >>> LineType('bus') in LineType('')
        True
        >>> LineType('') in LineType('bus')
        False
        >>> LineType('bus') in LineType('bus')
        True

    You can cast a :py:class:`LineType` to string if needed:

    .. code-block:: python

        >>> str(LineType('train.local'))
        'train.local'


.. py:class:: LineTypes(include=('', ), exclude=())

    A selector for :py:class:`LineType` object. It is defined as a list of included line types and a list of excluded linetypes. By default, all line types are included.

    .. code-block:: python

        >>> LineType('bus') in LineTypes()
        True

        >>> LineType('bus') in LineTypes(exclude=('bus', ))
        False
        >>> LineType('bus.express') in LineTypes(exclude=('bus', ))
        False
        >>> LineType('bus') in LineTypes(exclude=('bus.express', ))
        True
        >>> LineType('bus.express') in LineTypes(exclude=('bus.express', ))
        False

        >>> LineType('train') in LineTypes(include=('bus', ), exclude=('bus.express', ))
        False
        >>> LineType('bus') in LineTypes(include=('bus', ), exclude=('bus.express', ))
        True
        >>> LineType('bus.express') in LineTypes(include=('bus', ), exclude=('bus.express', ))
        False

    You can modify the selector using the following methods:

    .. method:: include(*linetypes)

        :param linetypes: one or more line types as string or :py:class:`LineType`

        Make sure that the given line types and all of their subtypes are matched by the selector.

    .. method:: exclude(*linetypes)

        :param linetypes: one or more line types as string or :py:class:`LineType`

        Make sure that the given line types and all of their subtypes are not matched by the selector.


.. py:class:: WayType(name)

    Each :py:class:`Way` has a line type. A Linetype has one of the values ``walk``, ``bike``, ``car``, ``taxi``.

    All identical way types are the same instance:

    .. code-block:: python

        >>> WayType('walk') is WayType('walk')
        True

.. py:class:: WayEvent(name, direction)

    A way :py:class:`Way` events one of the names ``stairs``, ``escalator`` or ``elevator`` and one of the directions ``up`` or ``down``.

    All identical way types are the same instance:

    .. code-block:: python

        >>> WayType('escalator', 'down') is WayType('escalator', 'down')
        True

    **The attributes can not be set.**

    .. attribute:: name

        ``stairs``, ``escalator`` or ``elevator``

    .. attribute:: direction

        ``up`` or ``down``
