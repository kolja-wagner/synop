# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 12:42:43 2025

@author: Kolja
"""

from pathlib import Path
from urllib.parse import urlencode
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

import requests

path_data = Path(__file__).parent.parent.joinpath("data", "ogimet", "synop")
path_data.mkdir(exist_ok=True)


# https://www.ogimet.com/cgi-bin/getsynop?begin=202312150000&end=202312152359&state=Germany&header=yes
URL = "https://www.ogimet.com/cgi-bin/getsynop?"


@dataclass
class SynopParam:
    begin: datetime
    end: datetime = None
    
    state: str = None
    block: int = None
    lang: str = "eng"
    header: str = "yes"
    
    filename: str = None
    
    def __post_init__(self):
        # todo: handle filename if still None.
        pass
    
    @classmethod
    def block_full_year(cls, block: int, year: int, **kwargs):
        begin = datetime(year, 1,1)
        end = datetime(year+1, 1,1) - timedelta(seconds=1)
        filename = kwargs.pop("filename", None) or f"WMO{block}_{year}.csv"
        return cls(begin=begin, end=end, block=block, filename=filename, **kwargs)
    
    @classmethod
    def state_full_day(cls, state: str, date: datetime, **kwargs):
        filename = kwargs.pop("filename", None) or f"{state}_{date.strftime('%Y%m%d')}.csv"        
        return cls(state=state, begin=date, end=date+timedelta(days=1), filename=filename, **kwargs)

    @staticmethod
    def dformat(datetime) -> str:
        return datetime.strftime("%Y%m%d%H%M")
    
    def encode(self) -> str:
        data = {k: v for k,v in asdict(self).items() if v is not None}
        data["begin"] = self.dformat(data["begin"])
        data["end"] = self.dformat(data["end"])
        return urlencode(data)



URL = "https://www.ogimet.com/cgi-bin/getsynop?"

def save_request(param):
    path_result = path_data.joinpath(param.filename)
    if path_result.exists():
        print(f"data found, request skipped {path_result}")
        return
    
    with requests.get(URL+param.encode()) as res:
        res.raise_for_status()
        path_result.write_text(res.text, encoding="utf-8")
    print(f"saved @ {path_result}")
    
    
    
def test():
    r1 = SynopParam.block_full_year(10338, 2024)
    r1 = SynopParam.state_full_day("Germany", datetime(2024,8,1))
    save_request(r1)

if __name__ == "__main__":
    test()
