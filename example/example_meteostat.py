# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 12:10:17 2025

@author: Kolja
"""
#
# https://dev.meteostat.net/python/
# Great tool but limitit variables

# Import Meteostat library and dependencies
from datetime import datetime
import matplotlib.pyplot as plt
from meteostat import Point, Daily, Stations, Hourly



from synop import Location


loc = Location.by_wmo(10338)


loc = Stations().nearby(loc.lat, loc.lon).fetch(1)#.iloc[0]


# # Set time period
start = datetime(2018, 1, 1)
end = datetime(2018, 12, 31)

# # Create Point for Vancouver, BC
# vancouver = Point(49.2497, -123.1193, 70)

# # Get daily data for 2018
data = Hourly(loc, start, end)
data = data.fetch()

# # Plot line chart including average, minimum and maximum temperature
# data.plot(y=['tavg', 'tmin', 'tmax'])
data.plot(y=["pres"])
# plt.show()