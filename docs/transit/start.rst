Getting Started
===============

The Transit Data Model
----------------------

Before we start using transit, you have to understand its underlying Models.

**Stop**
    A Stop is a group of Platforms (e.g. Berlin Hbf).

**Platform**
    A Platform is a place where a rides stop. (e.g. Gleis 7) It belongs to one Stop.

**Ride**
    A Ride is the journey of a bus/train/etc. It only happens once. Even the “same” ride on the next day is handled as another Ride.

**Line**
    A Line is a name for a group of Rides (e.g. Bus Line 495). Every Ride belongs to one Line.

**Trip**
    A Trip is a connection between two Stops (or AbstractLocations to be precise, see below) with rides, interchanges and/or footpaths in between.

The models **Stop**, **Adress** and **POI** (Point of Interest) are all subclasses of **Location** which describes a stand-alone Location with City and Name

Also, **Location** and **Platform** are subclasses of **AbstractLocation** which describas anything that has a static position.

Those models are called **Searchables** because you can search for them with transit. You can…

 * provide an instance of them. transit will try to retrieve it and return a more complete version of it to you
 * use their ``Request`` submodel to specify what you are looking. transit will use the ``Result`` submodel to give you the search results.

Other Models that are part of transit but can not be searched for include:

**Way**
    A path between two AbstractLocation objects.

**TimeAndPlace**
    A time and place object describes the time, stop and platform and coordinates where a ride meets a stop.

**RideSegment**
    In most cases, we are only interested in a part of a Ride – from where you enter the train/bus/etc. to where you leave it.
    That part is called a RideSegment – it consists of a Ride and the start and end point of the segment.

**RealtimeTime**
    Points in time are always given as a RealtimeTime object, which consists of a datetime and a delay (if known).

**Coordinates**
    Each ``AbstractLocation`` may have Coordinates. They consist of latitude and longitude.

**WayType**
    Each Way has a waytype. A WayType has one of the values ``walk``, ``bike``, ``car`` or ``taxi``

**LineType**
    Each Line has a linetype. A Linetype has one of the values `` `` (empty string), ``train``, ``train.local``, ``train.longdistance``, ``train.longdistance.highspeed``,
    ``urban``, ``metro``, ``tram``, ``bus``, ``bus.regional``, ``bus.city``, ``bus.express``, ``suspended``, ``ship``, ``dialable``, or ``other``.

    An empty string means that it can be anyone of the other linetypes, The linetype ``bus`` means that it could be any of the bus-subtypes. The reason for this is that
    not all networks differentiate between some subtyes (e.g. bus types). See the network reference for which linetypes it may output.

For more information, see `Model Reference`_.


Command Line Interface
----------------------

To get startet, let's look up Essen Hauptbahnhof in the VRR network using the command line interface.

To do so, we first have to describe Essen Hauptbahnhof as a ``Stop``:

.. code-block:: json

    ["Stop", {
      "name": "Essen Hauptbahnhof"
    }]

The outer list describes the data type (``Stop``) and the data.

Now we pass this data to the API. If you set the filename to ``-`` you can pass the data via STDIN.

.. code-block:: none

    transit vrr --output prettyjson essen.json

This sends the Stop to transit and it tries to get as much information as possible about that given stop with only one request to the server.

.. code-block:: json

    ["Stop",
      {
        "train_station_name": "Essen Hbf",
        "country": "de",
        "city": "Essen",
        "name": "Hauptbahnhof",
        "near_stops": {
          "results": [],
          "last_update": "2015-06-17 15:49:12"
        },
        "coords": [
          51.451137,
          7.012941
        ],
        "ids": {
          "ifopt": [
            null,
            "9289"
          ],
          "vrr": 20009289
        },
        "last_update": "2015-06-17 15:49:12",
        "rides": {  },
        "lines": {  }
      }
    ]

As you can see, the API returned a Stop with more information. Luckily for us, it even gave us the lines and rides attribute, which is not the case for all networks.

For more information about the command line syntax and available methods, see `Command Line Usage`_ and `Network API`_.

For more information about the JSON format, see `Model Reference`_ and `Model Serialization`_.

.. _`Command Line Usage`: cli.html
.. _`Network API`: api.html
.. _`Model Reference`: models.html
.. _`Model Serialization`: serializing.html

JSON Interface
--------------

If you want to process the data you want it in a easily parsable format and you want it complete. So let's do that and look at what we get.

.. code-block::

    transit VRR get_stop --json-noraw essen.json

Although this is the same type of data it is much more detailed.
First, we can see that the API returns a stop – the stop we gave as input – but with much more information.

**Stop**
    The stop now is defined by it's correct ``country``, ``city`` and ``name`` attribute.
    Also, we have its coordinates now. In the ``_ids`` attribute you can find its ids.
    This ID would be enough to identify the stop. Our input JSON could also have been ``["Stop", {"_ids": {"vrr": 20009289}}]`` with the same result.

**Line**
    In the ``lines`` attribute all lines that can be reached from this stop are listed. In this excerpt, only one line is listed.
    Note that in its ``last_stop`` attribute the stop is not fully described: The ``city`` attribute is missing.
    **Every attribute that has no data available will be missing.**
    To get the full information about this Stop, you would also pass it to the ``get_stop`` method.

In the ``rides`` attribute the next rides that pass this station are listed. To understand this, let's talk about how rides work:

**RideSegment**
    A ride is a journey of a train, bus, or similar from its first stop to its last stop.
    In most cases, we are only interested in a part of this journey – from where you enter the train/bus/etc. to where you leave it.
    That part is called a RideSegment – it consists of a ``ride`` and the start (``origin``) and end (``destination``) point of the segment.

**Ride**
    A ride primarily consists of a list of TimeAndPlace objects. Mosts of the time not all stops of the ride are known.
    This is why the ride in this example only consists of 3 TimeAndPlace objects, the origin of the ride, our stop and the destination of the ride.
    The ``null`` items in between them mean that there may be missing stops between.
    If the TimeAndPlace object directly before and after the ``null`` items are about the same stop, they might be the same.
    To get all information about a ride, use the ``get_ride`` method.

    Our stop is also listed in the ride. Because it is listed as a indirect child of itself, it gets the ``"is_truncated": true`` parameter.
    This means that objects that can lead to more children will not be listed. Here, the ``lines`` and ``rides`` attributes are empty lists.

**TimeAndPlace**
    A time and place object describes the time, stop and platform and coordinates where a ride meets a stop.

**RealtimeTime**
    Points in time are always given as a RealtimeTime object.
    A real time time object consists of a ``time`` attribute, which is always a ``datetime`` object in the ``YYYY-MM-DD HH:MM`` format and an optional ``delay`` attribute, which is the currently expected delay as a ``timedelta`` object in seconds.

    If the ``delay`` attribute is missing, no real time data is available. If the ride is on time the delay will be 0 seconds.

For more information about the JSON format, see `Model Reference`_ and `Model Serialization`_.

Python Interface
----------------

Let's see how you would access this via the Python interface. **Every attribute that has no data available will be None.**

.. code-block:: python

    from transit.models import Stop
    import transit.networks

    essen = Stop(name='Essen Hauptbahnhof')
    vrr = networks.network('VRR')

    essen = vrr.get_stop_rides(essen)
    print(essen.city)  # Essen
    print(essen.name)  # Hauptbahnhof

    # iterates through all lines
    for line in essen.lines:
        print(line.shortname)  # RB40 and similar

    # iterates through all rides
    for ridesegment in essen.rides:
        ride = ridesegment.ride

        print(ride.number)  # train number or similar
        print(ride.line.shortname)  # 106 or similar

        # all Ride attributes can also accessed using the RideSegment
        print(ridesegment.number)  # same as ride.number

        # iterate through all stops of the RideSegment
        for timeandplace in ridesegment:
            if timeandplace is not None:  # this is not a gap
                if timeandplace.departure is not None:  # we now the departure
                    print(timeandplace.departure.time)  # planned time as datetime.datetime
                    print(timeandplace.departure.delay)  # expceted delay as datetime.datetimeplanned time as datetime.datetime
                    print(timeandplace.departure.is_live)  # shortcut for delay is not None
                    print(timeandplace.departure.livetime)  # expceted time if real time information is available, otherwise planned time
                print(timeandplace.stop.name) # Hauptbahnhof or similar

        # iterate through all stops of the Ride
        for timeandplace in ridesegment.ride:
            # same as above, but without boundaries

        # you can also slice a ride or ride segment to get another ride segment
        newsegment = ridesegment.ride[1:]

For more information, see `Network API`_ and `Model Reference`_.
