#

from dataclasses import dataclass
from pathlib import Path

import requests
import pandas as pd
import numpy as np
from datetime import datetime

PATH_STATION_CSV    = Path(__file__).parent.joinpath("data","ogimet_stations_germany.csv")
PATH_STATION_CSV.parent.mkdir(exist_ok=True)
STATION_TABLE = None


@dataclass
class Location:
    name: str
    lat: float
    lon: float
    
    alt: float = None
    wmo: int = None
    icao: int = None
    country: str = None
    
    def __post_init__(self):
        # fill missing data, if the name can be matched to the table
        rows = STATION_TABLE[STATION_TABLE["Name"].str.lower() == self.name.lower()]
        if len(rows) != 1:
            return 
        
        self.alt = self.alt or int(rows.iloc[0].Altitude)
        self.wmo = self.wmo or int(rows.iloc[0]["WMO INDEX"])
        self.icao = self.icao or rows.iloc[0]["ICAO"]
        self.country = self.country or rows.iloc[0]["Country"]
        
    @staticmethod
    def convert_table_row(row):
        row = row.drop(["WIGOS ID", "Established", "Closed"])
        data = {
            "name": row.Name,
            "country": row.Country,
            "lat": parse_coord_str(row.Latitude),
            "lon": parse_coord_str(row.Longitude),
            "alt": int(row.Altitude),
            "wmo": int(row["WMO INDEX"]),
            "icao": row.ICAO,
            }
        return data
    

    @classmethod
    def by_name(cls, name: str):
        if STATION_TABLE is None:
            raise FileNotFoundError(f"{PATH_STATION_CSV.resolve()} could not be loaded.")
        
        rows = STATION_TABLE[STATION_TABLE["Name"].str.lower() == name.lower()]
        if len(rows) == 0:
            raise LookupError(f"{name=} not found in STATION TABLE.")
        if len(rows) > 1:
            raise LookupError(f"{name=} found multiple times in STATION TABLE.\n"
                              f"This might mean the lookup file is broken.")
        data = cls.convert_table_row(rows.iloc[0])
        return cls(**data)
    
    @classmethod
    def by_wmo(cls, wmo_index):
        if STATION_TABLE is None:
            raise FileNotFoundError(f"{PATH_STATION_CSV.resolve()} could not be loaded.")
        
        rows = STATION_TABLE[STATION_TABLE["WMO INDEX"] == wmo_index]
        if len(rows) == 0:
            raise LookupError(f"{wmo_index=} not found in STATION TABLE.")
        if len(rows) > 1:
            raise LookupError(f"{wmo_index=} found multiple times in STATION TABLE.\n"
                              f"The names are {list(rows.Name)}")
        return cls.by_name(rows.iloc[0].Name)
        
    @classmethod
    def by_icao(cls, icao_id):
        if STATION_TABLE is None:
            raise FileNotFoundError(f"{PATH_STATION_CSV.resolve()} could not be loaded.")
        
        rows = STATION_TABLE[STATION_TABLE["ICAO"] == icao_id]
        if len(rows) == 0:
            raise LookupError(f"{icao_id=} not found in STATION TABLE.")
        if len(rows) > 1:
            raise LookupError(f"{icao_id=} found multiple times in STATION TABLE.\n"
                              f"The names are {list(rows.Name)}")
        return cls.by_name(rows.iloc[0].Name)
    
    @property
    def latitude(self):
        return self.lat
    
    @property
    def longitude(self):
        return self.lon

    @property
    def altitude(self):
        return self.altitude
        

def load_station_table():
    table = pd.read_csv(PATH_STATION_CSV)
    assert table.shape[1] == 10
    return table

try:
    STATION_TABLE = load_station_table()
except Exception as e:
    print(f"[location] station table not loaded because of {type(e).__name__}."
          f"Run the download script again and reload the module.\n\n{e}")

def dec_to_ang(dec: float) -> (int, int, float):
    """ Convert decimal angle to deg/sec/min-tuple. """
    d = int(dec)
    m = int((dec - d)*60)
    s = (dec - d - (m/60)) * 3600
    return d, m, s

def ang_to_dec(deg: int, m: int=0, s: float=0) -> float:
    """ Convert deg/sec/min-tuple to decimal degree. """
    return deg + (m/60) + (m/3600)

def parse_coord_str(coord_str):
    parts = (int(v) for v in coord_str[:-1].split("-"))
    value = ang_to_dec(*parts)
    factor = +1 if coord_str[-1] in ("N", "E") else -1
    return factor*value






Location.by_name("Hannover")
