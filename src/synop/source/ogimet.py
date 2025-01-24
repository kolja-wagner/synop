# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 20:34:17 2025

@author: Kolja
"""
from pathlib import Path
import logging
import http
from urllib.parse import urlencode

import pandas as pd
import httpx
import io
from datetime import datetime, timedelta

from dataclasses import dataclass, asdict

from synop.path import PATH_DATA, path_station, path_synop

logger = logging.getLogger(__name__)

URL_SYNOP    = "https://www.ogimet.com/cgi-bin/getsynop?"
URL_STATIONS = "https://www.ogimet.com/display_stations.php?"

def url_station(state=None, name=None, wmo=None, icao=None, logic="AND"):   
    if all((state is None, name is None, wmo is None, icao is None)):
        raise ValueError("At least one parameter has to be set.\n\t"
                         "Choose 'state', 'name', 'wmo' and/or 'icao'")
    data = {"lang": "en",
            "tipo": logic,
            "isyn": wmo,
            "oaci": icao,
            "nombre": name,
            "estado": state,
            "Send": "Send"}
    data = {k:v for k, v in data.items() if v is not None}
    return URL_STATIONS + urlencode(data)


@dataclass
class SYNOP:
    begin: datetime
    end: datetime = None
    
    state: str = None
    block: int = None
    lang: str = "eng"
    header: str = "yes"
        
    @classmethod
    def block_full_year(cls, block: int, year: int, **kwargs):
        begin = datetime(year, 1,1)
        end = datetime(year+1, 1,1) - timedelta(seconds=1)
        return cls(begin=begin, end=end, block=block,  **kwargs)
    
    @classmethod
    def state_full_day(cls, state: str, date: datetime, **kwargs):
        return cls(state=state, begin=date, end=date+timedelta(days=1), **kwargs)

    @staticmethod
    def dformat(datetime) -> str:
        return datetime.strftime("%Y%m%d%H%M")
    
    def encode(self) -> str:
        data = {k: v for k,v in asdict(self).items() if v is not None}
        data["begin"] = self.dformat(data["begin"])
        data["end"] = self.dformat(data["end"])
        return urlencode(data)
    
    def get_path(self):
        return path_synop(self.state, self.block, self.begin, self.end)
    
    def get_url(self):
        return URL_SYNOP + self.encode()

class OGIMET:
    
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
    
    def get_request(self, url, form="text"):
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
    
    def request_stations(self, state=None, name=None, wmo=None, icao=None):
        url = url_station(state, name, wmo, icao)
        path_csv = path_station(state, name, wmo, icao)
        
        result = self.get_request(url, form="text")
        # testing: save raw result
        # path_csv.with_suffix(".html").write_text(result)
        # result = path_csv.with_suffix(".html").read_text()
        
        table = pd.read_html(io.StringIO(result), na_values=("----", '-----' ),
                             converters={"Established": lambda v: datetime.strptime(v, "%Y-%m-%d"), 
                                         "Closed": lambda v: datetime.strptime(v, "%Y-%m-%d")}
                             )[1]
        table.to_csv(path_csv, index=False)
        return table
    
    def request_synop(self, synop: SYNOP, reload=False):
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
