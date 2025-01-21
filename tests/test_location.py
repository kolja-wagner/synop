# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 22:31:30 2025

@author: Kolja
"""

from synop import Location

def test_loading():
    
    l1 = Location.by_name("Hannover") 
    l2 =  Location.by_wmo(10338)
    l3 = Location.by_icao("EDDV")
    
    assert l1 == l2
    assert l1 == l3
