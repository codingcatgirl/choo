Network API
===========

Available Methods
-----------------

.. py:method:: get_stop(stop)**

    Get all information about this stop you can get with one request.
    
    :param stop: Stop
    :rtype: :py:class:`Stop`
    :rtype: :py:class:`SearchResults` of :py:class:`Stop` with match score
    
    
.. py:method:: get_stop_rides(stop)**

    Get the next rides from this stop.
    
    :param stop: Stop
    :rtype: :py:class:`Stop` with ``rides`` attribute or :py:class:`SearchResults` with match score


Supported Networks
------------------

**VRR**
    The **EFA** API of the **Verkehrsverbund Rhein Ruhr** in Germany.
    
    Information for NRW is available, but real time data for local operators only in the VRR area.