# -*- coding: utf-8 -*-
"""
This module can be used to request data from https://www.ogimet.com/.

Note: 
    Please read the limitations stated under https://www.ogimet.com/getsynop_help.phtml.en

@author: Kolja
"""
import io
import logging
import http
from urllib.parse import urlencode
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

import pandas as pd
import httpx

from synop.path import path_station, path_synop

logger = logging.getLogger(__name__)


URL_STATIONS: str = "https://www.ogimet.com/display_stations.php?"
""" Base url for retrieving station data from ogimet.com."""

URL_SYNOP: str    = "https://www.ogimet.com/cgi-bin/getsynop?"
""" Base url for retrieving synop data from ogimet.com."""

@dataclass
class STATION_PARAM:
    """ dataclass to represent the parameter for a STATION request from ogimet.com.
    The attribute represent the parameter for filtering the database.
    At least one of the optional parameters has to be set.
    
    Attributes:
        state (str, optional):   If given state/territory contains, or is equal to the string.
        name (str, optional):    If given station name contains, or is equal to the string.
        wmo (int, optional):     if given synop WMO index contains, or is equal to the integer.
        icao (str, optional):    If given ICAO index contains, or is equal to the string.
        logic (str, optional):   Whether all ("AND") or one ("OR") condition has to be true.
    """
    state: str = None
    name: str = None
    wmo: int = None
    icao: int = None
    logic: str = "AND"
    
    def __post_init__(self):
        if all((self.state is None, self.name is None, self.wmo is None, self.icao is None)):
            raise ValueError("At least one parameter has to be set.\n\t"
                             "Choose 'state', 'name', 'wmo' and/or 'icao'")    

    def encode(self) -> str:
        """ encode the parameter to be used within the url."""
        data = {"lang": "en",
                "tipo": self.logic,
                "isyn": self.wmo,
                "oaci": self.icao,
                "nombre": self.name,
                "estado": self.state,
                "Send": "Send"}
        data = {k:v for k, v in data.items() if v is not None}
        return urlencode(data)
    
    def get_url(self) -> str:
        """ construct the url with :meth:`encode` and :const:`URL_STATIONS`."""
        return URL_STATIONS + self.encode()
    
    def get_path(self):
        """ construct file path with :func:`synop.path.path_station`."""
        return path_station(self.state, self.name, self.wmo, self.icao)


@dataclass
class SYNOP_PARAM:
    """ dataclass to represent the parameter for a SYNOP request from ogimet.com.
        
    Attributes:
        begin (datetime):   The starting time of the request.
        end (datetime, optional): The end time of the request. If not given the current time is inserted.
        state (int, optional):    The begin of the state string.
        block (str, optional):    The begin of the WMO index.
        lang (str, optional):     The language, default is "en".
        header (str, optional):   Whether to include the column names.
    """
    begin: datetime
    end: datetime = None
    
    state: str = None
    block: int = None
    lang: str = "eng"
    header: str = "yes"
        
    @classmethod
    def block_full_year(cls, block: int, year: int, **kwargs) -> "SYNOP_PARAM":
        """ Factory function to request a full year of synop data for a block.

        Parameters
        ----------
        block : int
            The WMO Index.
        year : int
            The year to be requested.
        **kwargs : 
            Additional keywords are given to the default init-method.
        """        
        begin = datetime(year, 1,1)
        end = datetime(year+1, 1,1) - timedelta(seconds=1)
        return cls(begin=begin, end=end, block=block,  **kwargs)
    
    @classmethod
    def state_full_day(cls, state: str, date: datetime, **kwargs) -> "SYNOP_PARAM":
        """ Factory function to request a day of synop data for all functions of a state.
         
        Parameters
        ----------
        state : str
            The beginning of the state of the station.
        date : datetime
            The date to be requested.
        **kwargs : TYPE
            Additional keywords are given to the default init-method.
        """
        return cls(state=state, begin=date, end=date+timedelta(days=1), **kwargs)

    @staticmethod
    def dformat(datetime) -> str:
        return datetime.strftime("%Y%m%d%H%M")
    
    def encode(self) -> str:
        """ encode the data to be used in the url."""
        data = {k: v for k,v in asdict(self).items() if v is not None}
        data["begin"] = self.dformat(data["begin"])
        data["end"] = self.dformat(data["end"])
        return urlencode(data)
    
    def get_url(self):
        """ construct the url with :meth:`encode` and :const:`URL_SYNOP`."""
        return URL_SYNOP + self.encode()    
    
    def get_path(self):
        """ construct file path with :func:`synop.path.path_synop`."""
        return path_synop(self.state, self.block, self.begin, self.end)
    

class OGIMET:
    """ A class to contain request functions for ogimet.com.
    
    Implements retrieving SYNOP and STATION data.    
    """
    
    def __init__(self):
        pass
    
    @property
    def headers(self):
        return {}
        
    @staticmethod    
    def handle_http_status(status):
        code = http.HTTPStatus(status)
        if not code.is_success:
            logger.error(code.description)
        return code.is_success  
    
    def get_request(self, url, form="text") -> str:
        """ a generic get request method.
        """
        try: 
            with httpx.Client(headers=self.headers) as client:
                response = client.get(url)
                if not self.handle_http_status(response.status_code):
                    return None
                if form == "text":
                    return response.text
                if form == "json":
                    return response.json()
                raise ValueError("{form=} not supported for method 'get_request'. Choose ['text', 'json'].")
        except Exception as e:
            logger.error(f"GET request failed for {url}\n\t{e}")
            return None
    
    def request_stations(self, param: STATION_PARAM) -> pd.DataFrame:
        """
        Send, convert and save a Station request from ogimet.com.

        Parameters
        ----------
        param : STATION_PARAM
            The parameter are described in the :class:`STATION_PARAM`.

        Returns
        -------
        table : pd.DataFrame
            Returns a Dataframe with a list of stations. The data is saved within the 
            :const:`synop.path.PATH_DATA` directory.
        """
        path_csv = param.get_path()
        result = self.get_request(param.get_url(), form="text")
        # testing: save raw result
        # path_csv.with_suffix(".html").write_text(result)
        # result = path_csv.with_suffix(".html").read_text()
        
        table = pd.read_html(io.StringIO(result), na_values=("----", '-----' ),
                             converters={"Established": lambda v: datetime.strptime(v, "%Y-%m-%d"), 
                                         "Closed": lambda v: datetime.strptime(v, "%Y-%m-%d")}
                             )[1]
        table.to_csv(path_csv, index=False)
        return table
    
    def request_synop(self, synop: SYNOP_PARAM, reload: bool = False) -> pd.DataFrame:
        """
        Send, convert and save a synop request from ogimet.com.
        
        Parameters
        ----------
        synop : SYNOP_PARAM
            The parameter are described in the :class:`SYNOP_PARAM`.
        reload : bool, optional
            If true the data is requested even if a file is already exists. The default is False.

        Returns
        -------
        table : pd.DataFrame
            Returns a Dataframe with a list of unparsed synop reports, with timestamp and wmo id.
            The data is saved within the :const:`synop.path.PATH_DATA` directory.
        """
        url = synop.get_url()
        path_csv = synop.get_path()
        
        if path_csv.is_file() and not reload:
            logger.debug("[synop request] load from file")
            return pd.read_csv(path_csv)
        
        logger.debug("[synop request] retrieve data")

        result = self.get_request(url, form="text")
        # testing: save raw data
        # path_csv.write_text(result, encoding="utf-8")
        # result = path_csv.read_text()
        
        cols = ("station", "year","month","day", "hour", "minute", "synop")
        df = pd.read_csv(io.StringIO(result), names=cols, skiprows=1)
        df["time"] = pd.to_datetime(df.drop(["station", "synop"], axis=1))
        df = df.drop(["year","month", "day", "hour", "minute"], axis=1)
        df.to_csv(path_csv, index=False)
        logger.debug(f"[synop request] saved at {path_csv}")
        return df
