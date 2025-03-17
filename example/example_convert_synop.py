# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 13:36:28 2025

@author: Kolja
"""
from pathlib import Path
from pymetdecoder.synop import SYNOP
from pymetdecoder import DecodeError
from synop import Location
import pandas as pd
import numpy as np
import xarray as xr
s = SYNOP()

path_data = Path("data/ogimet/synop/SYNOP_10338_202401010000_202412312359.csv")
# path_data = Path("data/ogimet/synop/SYNOP_Germany_202408010000_202408020000.csv")
from tqdm import tqdm


def extract_value(data, name):
    section = data.get(name)
    value = section.get("value", None) if section else None
    unit = section.get("unit", None) if section else None
    return xr.DataArray([[value]], 
                 dims = ("time", "station"),
                 name=name,
                 attrs=dict(units=unit)
                 )
    

def synop_dataset(entry: pd.Series):
    try:
        data = s.decode(entry["synop"])
    except DecodeError:
        return xr.Dataset()
    values = {
        val: extract_value(data, val) for val in ["wind_indicator", 
                                             "precipitation_indicator", 
                                             "weather_indicator",
                                             "visibility",
                                             "cloud_cover",
                                             "air_temperature",
                                             "dewpoint_temperature",
                                             "station_pressure",
                                             "sea_level_pressure",
                                             # "pressure_tendency",
                                             # "sunshine",
                                             ]
                                             
                                             }

    return xr.Dataset(data_vars=values, 
                      coords=dict(time=[entry["time"]],
                                  station=[int(entry["station"])]
                                  )
                      )
    
def synop_dataset_series(series: pd.Series):
    
    if len(series.time.unique()) == 1:
        return xr.concat((synop_dataset(e) for _, e in tqdm(series.iterrows())), dim="station")

    if len(series.station.unique()) == 1:
        return xr.concat((synop_dataset(e) for _, e in tqdm(series.iterrows())), dim="time")
    
    return xr.merge([synop_dataset(e) for _, e in tqdm(series.iterrows())],)


entrys = pd.read_csv(path_data, parse_dates=["time"])#.iloc[slice(1000)]
ds = synop_dataset_series(entrys)
ds
#%%
# ds.cloud_cover.plot.scatter(x="time", edgecolor="None")
# [SYNOP().decode(t["Synop"])["air_temperature"]["value"] 
[SYNOP().decode(t.synop) for i, t in entrys.iloc[:10].iterrows()][9]["radiation"]






















