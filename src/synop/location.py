# -*- coding: utf-8 -*-
from dataclasses import dataclass
import pandas as pd

from synop.path import PATH_DEFAULT_STATIONS

STATION_TABLE: pd.DataFrame = None
""" The lookup table, loaded from :const:`PATH_DEFAULT_STATIONS`. If the file is missing,
a script is provided within the ``tools/`` directory."""

@dataclass
class Location:
    """
    Represents a location.

    Attributes:
        name (str): The name of the location.
        lat (float):  The latitude of the location in degrees (N:+, S:-) 
        lon (float):  The longitude of the location, in degrees (E:+, W:-)
        
        alt (float, optional): The altitude of the location, in m (above sea level).
        wmo (int, optional):   The WMO Index, if the location is a station.
        icao (str, optional):  The ICAO Id, if the location is a station.
        country (str, optional): The country of the station.
        
    After the init function the station name is looked up within the :const:`STATION_TABLE` and 
    all optional values are filled if they are not defined previously.
    """
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
        """
        Alternatative creation method from a given name.
        The data is populated from the :const:`STATION_TABLE`.

        Parameters
        ----------
        name : str
            The name of the station, that has to be matched exactly to one entry of the table.

        Raises
        ------
        FileNotFoundError
            raises if the :const:`STATION_TABLE` was not loaded.
        LookupError
            raises if the lookup doesn't return exactly one row of the table.

        Returns
        -------
        Location
            A :class:`Location` that is generated from the :const:`STATION_TABLE`.
        """
        if STATION_TABLE is None:
            raise FileNotFoundError(f"{PATH_DEFAULT_STATIONS.resolve()} could not be loaded.")
        
        rows = STATION_TABLE[STATION_TABLE["Name"].str.lower() == name.lower()]
        if len(rows) == 0:
            raise LookupError(f"{name=} not found in STATION TABLE.")
        if len(rows) > 1:
            raise LookupError(f"{name=} found multiple times in STATION TABLE.\n"
                              f"This might mean the lookup file is broken.")
        data = cls.convert_table_row(rows.iloc[0])
        return cls(**data)
    
    @classmethod
    def by_wmo(cls, wmo_index: int):
        """ 
        Alternative creation method from a given station id.
        Retrieves a name and uses the :meth:`by_name` method.
        
        Parameters
        ----------
        wmo_index : int
            The index of the station, that has to be matched exactly to one entry of the table.

        Raises
        ------
        FileNotFoundError
            raises if the :const:`STATION_TABLE` was not loaded.
        LookupError
            raises if the lookup doesn't return exactly one row of the table.

        
        Returns
        -------
        Location
           A :class:`Location` generated from the :const:`STATION_TABLE` data.
        """
                
        if STATION_TABLE is None:
            raise FileNotFoundError(f"{PATH_DEFAULT_STATIONS.resolve()} could not be loaded.")
        
        rows = STATION_TABLE[STATION_TABLE["WMO INDEX"] == wmo_index]
        if len(rows) == 0:
            raise LookupError(f"{wmo_index=} not found in STATION TABLE.")
        if len(rows) > 1:
            raise LookupError(f"{wmo_index=} found multiple times in STATION TABLE.\n"
                              f"The names are {list(rows.Name)}")
        return cls.by_name(rows.iloc[0].Name)
        
    @classmethod
    def by_icao(cls, icao_id):
        """ 
        Alternative creation method from a given ICAO id.
        Retrieves a name and uses the :meth:`by_name` method.
        
        Parameters
        ----------
        icao_id : int
            The ICAO ID of the station, that has to be matched exactly to one entry of the table.

        Raises
        ------
        FileNotFoundError
            raises if the :const:`STATION_TABLE` was not loaded.
        LookupError
            raises if the lookup doesn't return exactly one row of the table.

        Returns
        -------
        Location
           A :class:`Location` generated from the :const:`STATION_TABLE` data.
        """
        if STATION_TABLE is None:
            raise FileNotFoundError(f"{PATH_DEFAULT_STATIONS.resolve()} could not be loaded.")
        
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
        


def dec_to_ang(dec: float) -> (int, int, float):
    """ Convert decimal angle to deg/sec/min-tuple. """
    d = int(dec)
    m = int((dec - d)*60)
    s = (dec - d - (m/60)) * 3600
    return d, m, s

def ang_to_dec(deg: int, m: int=0, s: float=0) -> float:
    """ Convert deg/sec/min-tuple to decimal degree. """
    return deg + (m/60) + (m/3600)

def parse_coord_str(coord_str: str) -> float:
    """ Parse the format used in the :const:`STATION_TABLE` to a floating value.
    Uses the :func:`ang_to_deg` function internally.
    """
    parts = (int(v) for v in coord_str[:-1].split("-"))
    value = ang_to_dec(*parts)
    factor = +1 if coord_str[-1] in ("N", "E") else -1
    return factor*value

def load_station_table():
    """ The loading function to populate :const:`STATION_TABLE` from :const:`PATH_DEFAULT_STATIONS`"""
    table = pd.read_csv(PATH_DEFAULT_STATIONS, parse_dates=[8,9])
    assert table.shape[1] == 10
    return table

try:
    STATION_TABLE = load_station_table()
except Exception as e:
    print(f"[location] station table not loaded because of {type(e).__name__}."
          f"Run the download script again and reload the module.\n\n{e}")

