Command Line Usage
==================

Syntax
------

.. code-block::
    
    transit networks
    transit methods
    transit <network> <method> [ --json | --nojson | --json-noraws ] <filename0> [ <filename1> [ … ] ]

**transit networks:**
    Outputs a JSON list of supported networks.
    
**transit methods:**
    Outputs a JSON dictionary of supported methods with method names as names and list of needed arguments.
    
**transit <network> <method>:**
    Calls a method and outputs its result. By default, the output is human readable, (``--nojson``).
    Use ``--json`` to get JSON output or ``--json-noraws`` to get JSON output with no raw data (smaller size).
    
    Filenames can also be ``-``, to read the data from STDIN. (every file should end with EOF)


Exit codes
----------

**0:**
    Everything went well, here's your output.

**1:**
    A Python exception occured. You gave invalid data or you discovered a bug.
    The output is the python exception.
    
**2:**
    Usage error (Unknown network, method or wrong argument count).
    You can find an error message in STDOUT.
    
**3:**
    Your input data is not valid and could not be loaded.
    
**4:**
    This method is not supported by this network.
