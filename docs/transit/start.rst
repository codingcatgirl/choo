Getting Started
===============

Command Line Interface
----------------------

To get startet, let's look up Essen Hauptbahnhof in the VRR network using the command line interface.

To do so, we first have to describe Essen Hauptbahnhof as a ``Stop``:

.. code-block:: json
    
    ["Stop", {
        "name": "Essen Hauptbahnhof"
    }]

The outer list describes the data type (``Stop``) and the data.

Now we pass this data to the API.

.. code-block:: none
    
    transit VRR get_stop essen.json
    
The API method ``get_stop`` tries to get as much information as possible about a given stop with only one request to the server.

.. code-block:: none

    Stop
      country: de
      city: Essen
      name: Hauptbahnhof
      coords: (51.451139, 7.012937)
      lines:
        RB40 → Hagen Hauptbahnhof (by Abellio Zug in vrr)
        RE 14 → Borken, Bahnhof (by None in owl)
        […]
      rides:
        13:11 +4   4     107 → Essen Bredeney
        13:13      3     SB16 → Bottrop Feldhausen Bf
        13:13      3     U18 → Essen Berliner Platz
        […]

As you can see, the API returned a Stop with more information. Luckily for us, it even gave us the lines and rides attribute, which is not guaranteed by the ``get_stop`` method.

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
    
The ``--json-noraw`` argument suppresses the raw data (XML or whatever the backend sends) in the JSON as it would make the output even larger. If you want to pass the json output back to the Interface, you should (but do not have to) use ``--json``.

For more information about the command line syntax and available methods, see `Command Line Usage`_ and `Network API`_.

If you set the filename to ``-`` you can pass the data via STDIN.

.. code-block:: json

    ["Stop", {
        "_ids": {"vrr": 20009289},
        "country": "de",
        "city": "Essen",
        "name": "Hauptbahnhof",
        "coords": ["tuple", [51.451139, 7.012937]],
        "lines": [
            ["Line", {
                "_ids": {},
                "name": "RB40",
                "product": "Abellio-Zug",
                "shortname": "RB40",
                "linetype": ["LineType", "localtrain"],
                "last_stop": ["Stop", {
                    "_ids": {"vrr": 20002007},
                    "country": "de",
                    "name": "Hagen Hauptbahnhof"
                }],
                "route": "Essen - Bochum - Witten - Hagen",
                "operator": "Abellio Zug",
                "network": "vrr"
            }]
        ],
        "rides": [
            ["RideSegment", {
                "origin": 2,
                "ride": ["Ride", {
                    "_ids": {"vrr": "vrr:11106: :R:j14"},
                    "number": "11106",
                    "stops": [
                        ["TimeAndPlace", {
                            "_ids": {},
                            "stop": ["Stop", {
                                "_ids": {},
                                "country": "de",
                                "name": "Essen Helenenstr. Schleife"
                            }]
                        }],
                        null,
                        ["TimeAndPlace", {
                            "_ids": {},
                            "departure": ["RealtimeTime", {
                                "_ids": {},
                                "time": ["datetime", "2014-12-15 13:24"],
                                "delay": ["timedelta", 120]
                            }],
                            "stop": ["Stop", {
                                "_ids": {"vrr": 20009289},
                                "lines": [],
                                "rides": [],
                                "coords": ["tuple", [51.451139, 7.012937]],
                                "is_truncated": true,
                                "city": "Essen",
                                "country": "de",
                                "name": "Hauptbahnhof"
                            }],
                            "platform": "1",
                            "coords": ["tuple", [51.449839, 7.01262]]
                        }],
                        null,
                        ["TimeAndPlace", {
                            "_ids": {},
                            "stop": ["Stop", {
                                "_ids": {"vrr": 20009832},
                                "country": "de",
                                "name": "Essen Altenessen Bf Schleife"
                            }]
                        }]
                    ],
                    "line": ["Line", {
                        "_ids": {},
                        "name": "Stra\u00dfenbahn 106",
                        "product": "Stra\u00dfenbahn",
                        "operator": "EVAG Strab",
                        "shortname": "106",
                        "linetype": ["LineType", "tram"],
                        "route": "Bergeborbeck - Helenenstr. - R\u00fcttenscheid - Essen Hbf - Altenessen",
                        "network": "vrr"
                    }]
                }],
            }]
        ]
    }]
    
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
    