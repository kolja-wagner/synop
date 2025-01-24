# -*- coding: utf-8 -*-
"""
This module defines the directory structure and common file name patterns.
It is a low level module and can be imported from anywhere within the synop package.

@author: Kolja
"""
from pathlib import Path
from datetime import datetime

PATH_DATA = Path(__file__).joinpath("..","..","..", "data").resolve()
""" The path, where the requested data will be stored. Used as cache."""
assert PATH_DATA.exists()

PATH_DEFAULT_STATIONS    = Path(__file__).parent.joinpath("data","STATIONS_Germany.csv")
""" The path where the lookup table data is stored."""
PATH_DEFAULT_STATIONS.parent.mkdir(exist_ok=True)


def path_station(state: str = None, name: str = None, wmo: int = None, icao: str = None) -> Path:
    """
    Generate a filename for a OGIMET-Station request. The schema is not completely unambiguous, 
    but covers the most used cases. The parameter are fully described in :func:`synop.source.ogimet.STATION_PARAM`.
    
    Scheme:
        ``PATH_DATA / ogimet / stations / STATIONS_<tags>.csv``
    
    Parameters
    ----------
    state : str, optional
        The state of the station. The default is None.
    name : str, optional
        The name of the station. The default is None.
    wmo : int, optional
        The WMO Index of the station. The default is None.
    icao : str, optional
        The ICAO tag of the station. The default is None.

    Returns
    -------
    Path
        A file path
    """
    tags = "_".join([str(s) for s in (state, name, wmo, icao) if s is not None])
    path = PATH_DATA.joinpath("ogimet", "stations", f"STATIONS_{tags}.csv")
    path.parent.mkdir(exist_ok=True)
    return path


def path_synop(state: str = None, block: int = None, begin: datetime = None, end: datetime = None) -> Path:
    """
    Generate a filename for a OGIMET-SYNOP request. The schema is not completely unambiguous, 
    but covers the most used cases. The parameter are fully described in :class:`synop.source.ogimet.SYNOP_PARAM`.
    
    Scheme:
        ``PATH_DATA / ogimet / synop / SYNOP_<tags>.csv``
    
    Parameters
    ----------
    state : str, optional
        The state of the stations. The default is None.
    block : str, optional
        The block of stations. The default is None.
    begin : datetime, optional
        The first time of the requested synop data. The default is None.
    end : datetime, optional
        The last time of the requested synop data. The default is None.

    Returns
    -------
    Path
        A file path
    """
    tags = "_".join((str(s) for s in (state, block) if s is not None))
    time = "_".join(dt.strftime("%Y%m%d%H%M") for dt in (begin, end))
    path = PATH_DATA.joinpath("ogimet", "synop", f"SYNOP_{tags}_{time}.csv")
    path.parent.mkdir(exist_ok=True)
    return path


