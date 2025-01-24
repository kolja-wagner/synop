# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 21:35:01 2025

@author: Kolja
"""
from pathlib import Path

PATH_DATA = Path(__file__).joinpath("..","..","..", "data").resolve()
assert PATH_DATA.exists()

PATH_DEFAULT_STATIONS    = Path(__file__).parent.joinpath("data","STATIONS_Germany.csv")
""" The path where the lookup table data is stored."""
PATH_DEFAULT_STATIONS.parent.mkdir(exist_ok=True)



def path_station(state=None, name=None, wmo=None, icao=None):
    tags = "_".join([str(s) for s in (state, name, wmo, icao) if s is not None])
    path = PATH_DATA.joinpath("ogimet", "stations", f"STATIONS_{tags}.csv")
    path.parent.mkdir(exist_ok=True)
    return path


def path_synop(state=None, block=None, begin=None, end=None):
    tags = "_".join((str(s) for s in (state, block) if s is not None))
    time = "_".join(dt.strftime("%Y%m%d%H%M") for dt in (begin, end))
    path = PATH_DATA.joinpath("ogimet", "synop", f"SYNOP_{tags}_{time}.csv")
    path.parent.mkdir(exist_ok=True)
    return path


