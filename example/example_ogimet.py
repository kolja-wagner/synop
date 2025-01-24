# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 22:34:11 2025

@author: Kolja
"""
from datetime import datetime
from synop import OGIMET, SYNOP_PARAM
        
def main():
    
    # test stations
    o = OGIMET()
    stations = o.request_stations(state="Germany")
    stations.info()
    
    # test full year
    s = SYNOP_PARAM.block_full_year("10338", 2024)#.url()
    table = o.request_synop(s, reload=False)
    table.info()
    
    # test full state    
    s = SYNOP_PARAM.state_full_day("Germany", datetime(2024,8,1))
    table = o.request_synop(s, reload=False)
    table.info()
    
    
if __name__ == "__main__":
    main()