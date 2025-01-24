# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 22:35:46 2025

@author: Kolja
"""
from pathlib import Path

import requests
import pandas as pd
import numpy as np

from synop.path import PATH_DEFAULT_STATIONS
from synop.source import OGIMET
from synop.location import load_station_table

def main():
    o = OGIMET()
    stations = o.request_stations(state="Germany")
    stations.to_csv(PATH_DEFAULT_STATIONS, index=False)
    
    result = load_station_table()
    
    if not stations.equals(result):
        print("[reload_station_table] table not equal")
        stations.info()
        result.info()
    else:
        print("[reload_station_table] redownload successfull.")
        

if __name__ == "__main__":
    main()
    
