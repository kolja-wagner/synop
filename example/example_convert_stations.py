# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 09:52:23 2025

@author: Kolja
"""

from pathlib import Path
import pandas as pd
import xarray as xr
path_files = Path("../data/ogimet/synop")
assert path_files.exists()


def csv_to_nc(path_inp, path_out):
    
    cols = ("station", "year","month","day", "hour", "minute", "synop")
    df = pd.read_csv(path_inp, names=cols, skiprows=1)
    df["time"] = pd.to_datetime(df.drop(["station", "synop"], axis=1))
    df = df.drop(["year","month", "day", "hour", "minute"], axis=1)
    # df = df.set_index(["station", "time"])
    
    pivot = df.pivot_table(index="time", columns="station", values="synop", aggfunc="first")
    da = xr.DataArray(pivot, dims=["time", "station"], name="synop")
    da.to_netcdf(path_out)
    print(f"saved @ {path_out}")
    return da

    
path_inp = path_files.joinpath("Germany_20240801.csv")
path_out = path_inp.with_suffix(".nc")
csv_to_nc(path_inp, path_out)
    

