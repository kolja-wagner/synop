# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 22:35:46 2025

@author: Kolja
"""
from pathlib import Path

import requests
import pandas as pd
import numpy as np

from synop.location import PATH_STATION_CSV, load_station_table

PATH_STATION_HTML   = Path(__file__).parent.joinpath("data","ogimet_stations_germany.html")
PATH_STATION_HTML.parent.mkdir(exist_ok=True)
URL_STATION         = "https://www.ogimet.com/display_stations.php?lang=en&tipo=AND&isyn=&oaci=&nombre=&estado=germany&Send=Send"
    
def request_ogimet_table():
    try:
        response = requests.get(URL_STATION)
        response.raise_for_status()
        PATH_STATION_HTML.write_text(response.text, encoding="utf-8")
        
    except requests.exceptions.RequestException as e:
        print(f"[location] An {type(e).__name__} occurred during the request.\n\n{e}")
    print(f"Request saved to {PATH_STATION_HTML}")

def convert_html_table():
    table = pd.read_html(PATH_STATION_HTML)[1]
    table["WMO INDEX"] = table["WMO INDEX"].replace('-----', np.nan).astype(float)
    table.to_csv(PATH_STATION_CSV, index=False)
    return table

def main():
    # request_ogimet_table()
    table = convert_html_table()
    assert table.equals(load_station_table())
    return table

if __name__ == "__main__":
    main()
    
