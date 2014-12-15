Model Serialization / JSON
==========================

All Models can be (un)serialized to/from a JSON-encodable format.

A list of all Models can be found in the `Model Reference`_.

.. _`Model Reference`: models.html

Here is how to construct the serialized representation of anything:

**model**
    All public attributes that are either not dynamic and not None or overwritten and the attributs ``_ids`` and ``_raws`` are put into a dictionary. All values are serialized.
    
    The result is a list consisting of the Model type as a string and the created dictionary.
    
    .. code-block:: json
    
        ["Stop", {
            "_ids": {"vrr": 20009289},
            "_raws": {},
            "country": "de",
            "city": "Essen",
            "name": "Hauptbahnhof",
            "coords": ["tuple", [51.451139, 7.012937]]
        }]
        
    * **Ride** objects get the attribute ``stops`` with a serialized list of ``TimeAndPlace`` objects and None items.
    * **LineType** objects do not generate a dictionary but the line type as a string.
    * **LineTypes** objects do not generate a dictionary but a list of included line types as strings.
    * **RideStopPointer** objects are treated as integers.
    
**dictionary, integer, float, string**
    Normal JSON representation.
    
**list, tuple**:
    A tuple consisting of the string ``list`` or ``tuple`` and a list of its serialized contents.
    
    .. code-block:: json
    
        ["tuple", [51.451139, 7.012937]]
    
**datetime**:
    A tuple consisting of the string ``datetime` and the datetime as YYYY-MM-DD HH:II.
    
    .. code-block:: json
    
        ["datetime", "2014-12-15 13:24"]
        
**timedelta**:
    A tuple consisting of the string ``timedelta` and the timedelta in seconds as an integer.
    
    .. code-block:: json
    
        ["timedelta", 120]
        
**None**:
    .. code-block:: json
    
        null