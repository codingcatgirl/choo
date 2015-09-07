Network Reference
=================

.. py:class:: API

    .. py:method:: query(obj)

        Pass a Searchable and it will return a Searchable from the API or None/null if it could not be found. Pass a Searchable.Request and you will get a corresponding Searchable.Results.


Network APIs
------------------

.. py:class:: EFA

    EFA is a public transport :py:class:`API` used world wide by many network operators.


Supported Networks
------------------

**VRR – Verkehrsverbund Rhein Ruhr** (``de.vrr`` :py:class:`EFA`)
    ifopt available. Also supports all of NRW and some parts of Germany.

**VRN – Verkehrsverbund Rhein-Neckar** (``de.vrn`` :py:class:`EFA`)
    ifopt available. Also supports some parts of Germany and Europe.
