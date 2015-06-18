Command Line Usage
==================

Syntax
------

The Transit Command Line api supports json and msgpack.

For msgpack support, the pip package ``msgpack-python`` has to be installed.

You can specify your input type with the flag ``--input json`` or ``--input msgpack`` (default is json).

You can specify your out type with the flag ``--output json`` or ``--output prettyjson`` (indented) or ``--output msgpack`` (default is json).

**transit networks**
    Outputs a list of supported networks.

**transit <network> <filename>**
    Passes the given object to the API.

    Filenames can also be ``-``, to read the data from STDIN.

For more information about supported networks and their supported queries, see `Network API`_.

For more information about the data input format, see `Model Serialization`_.

.. _`Network API`: api.html
.. _`Model Serialization`: serializing.html


Exit codes
----------

**0:**
    Everything went well, here's your output.

**1:**
    A Python exception occured. You gave invalid data or you discovered a bug.
    The output is the python exception.

**3:**
    Your input data is not valid and could not be loaded.

**4:**
    Your input data is not valid and could not be unserialized.

**5:**
    The network does not support this query type.
