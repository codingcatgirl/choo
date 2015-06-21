Transit API
===========

Use the transit API du access transit's capabilities from other programming languages.

* Each command starts with a keyword and is followed by a space and an argument.

* Each command gets a response.
* Each successful response starts with ``ok`` followed by a space and a data string in your selected data format.
* Each failed response starts with ``err`` followed by a space and an error message in plain text.

.. code-block:: none

    usage: transit [-h] [--cli] [--tcp] [--tcp-host TCP_HOST]
                   [--tcp-port TCP_PORT] [--ws] [--ws-host WS_HOST]
                   [--ws-port WS_PORT]

    optional arguments:
      -h, --help           show this help message and exit
      --cli                enable command line interface
      --tcp                enable tcp server
      --tcp-host TCP_HOST  set address to listen on (default: 0.0.0.0)
      --tcp-port TCP_PORT  set tcp port (default: random unused port)
      --ws                 enable websocket server
      --ws-host WS_HOST    set address to listen on (default: 0.0.0.0)
      --ws-port WS_PORT    set tcp port (default: random unused port)


API Interfaces
--------------

**Command Line**
    Communication over Standard Input/Output
    Commands and responses end with ``\n``.

**TCP**
    Communication over TCP
    Commands and responses end with ``\r\n``.

**Websockets**
    .. important::
        For websockets, the pip package ``websockets`` has to be installed.

    Communication over Websockets.
    Data format is automatically set to ``json``.


Available Commands
------------------

**format <format>**
    Set the data format: ``json`` or ``msgpack``

    .. important::
        For msgpack support, the pip package ``msgpack-python`` has to be installed.

    You have to set the format before and other command is accepted.

    Returns the selected format as a string.

**get networks**
    Returns the list of available networks. See _`Network Reference` for more information.

**network <network>**
    Set the network to use for querying.

    Returns the name of the selected network.

**query <query>**
    The argument has to be a serialized ``Searchable`` or ``Searchable.Request`` object in your selected data format.

    Returns the result.

.. _`Network Reference`: api.html
