Model Serialization / JSON
==========================

All choo models can be (un)serialized to/from a JSON-encodable format.

In Python
---------

.. code-block:: python

    from models import Stop, Location, Serializable
    # Create a Stop
    stop = Stop(city='Essen', name='Hauptbahnhof')

    # simple serialization
    serialized = stop.serialize()
    stop = Stop.unserialize(serialized)

    # possibly typed serialization
    # this will save the model type if the given object is a submodel
    serialized = Location.serialize(stop)
    stop = Location.unserialize(serialized)

    # this will be a simple serialization because the given Model is not a submodel
    serialized = Stop.serialize(stop)
    stop = Stop.unserialize(serialized)

    # always typed serialization
    serialized = Serializable.serialize(stop)
    stop = Serializable.unserialize(serialized)


How it works
------------

.. _`Model Reference`: models.html

.. caution::
    Some models have a non-dictionary representation or some additional attributes in their dictionary representation. See the `Model Reference`_ for more information.

All public attributes that are not dynamic and not ``None`` are put into a dictionary. All values are serialized.

| **datetime** values are respresented as a string in ``YYYY-MM-DD HH:II:SS`` format.
| **timedelta** values are respresented as a the total number of seconds as int.

.. code-block:: json

    {
        "_ids": {"vrr": 20009289},
        "country": "de",
        "city": "Essen",
        "name": "Hauptbahnhof",
        "coords": [51.451139, 7.012937]
    }

If the serialization is typed, the output is a two element list with name of the model and the constructed dictionary (or other respresentation).

.. code-block:: json

    ["Stop", {
        "_ids": {"vrr": 20009289},
        "country": "de",
        "city": "Essen",
        "name": "Hauptbahnhof",
        "coords": [51.451139, 7.012937]
    }]
