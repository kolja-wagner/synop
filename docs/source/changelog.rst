changelog
=========

Version 0.2
-----------
* Adding :mod:`synop.path` module to define directory structure and file name schemata.
* Update the request code in :mod:`synop.source.ogimet` module.
   * Adding :class:`synop.source.ogimet.STATION_PARAM` and :class:`synop.source.ogimet.SYNOP_PARAM` classes to define the parameter for data requests
   * Implement :class:`synop.source.ogimet.OGIMET` to handle data requests.
   * Store requested data in :const:`synop.path.PATH_DATA`
   * Update :mod:`synop.location` and ``tool/``
   
* Adding documentation to new modules/classes.

Version 0.1
-----------

* Implementing :class:`synop.location.Location` class to represent geolocations.
   * ``tool/``: request_station_table.py retrieves a list of all stations in germany and saves as csv lookup table.
   * the :meth:`synop.location.Location.by_name` method generates locations from the lookup table.
   * the :meth:`synop.location.Location.by_wmo` and :meth:`synop.location.Location.by_icao` uses this function.

* Added basic documentation structure
* Added first unit test cases    
    