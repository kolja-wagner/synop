changelog
=========

Version 0.1
-----------

* Implementing :class:`synop.location.Location` class to represent geolocations.
   * ``tool/``: request_station_table.py retrieves a list of all stations in germany and saves as csv lookup table.
   * the :meth:`synop.location.Location.by_name` method generates locations from the lookup table.
   * the :meth:`synop.location.Location.by_wmo` and :meth:`synop.location.Location.by_icao` uses this function.

* Added basic documentation structure
* Added first unit test cases    
    