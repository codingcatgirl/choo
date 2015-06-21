Network Reference
=================

.. py:class:: API

    .. py:method:: query(obj)

        Pass a Searchable and it will return a Searchable from the API or None/null if it could not be found. Pass a Searchable.Request and you will get a corresponding Searchable.Results.


Network Interfaces
------------------

.. py:class:: EFA

    EFA is a public transit :py:class:`API` used world wide by many network operators.


Supported Networks
------------------

.. py:class:: VRR

    The :py:class:`EFA` instance of the **Verkehrsverbund Rhein Ruhr** in Germany.

    Information for all of NRW is available, but real time data for local operators only in the VRR area.

    Some Information for the rest of Germany is also available.
