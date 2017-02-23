#!/usr/bin/env python
"""
http://wsprnet.org/drupal/downloads
"""
from matplotlib.pyplot import show
#
from weaksig_plot import readwspr,plotwspr

csvfn = 'data/wsprspots-2017-02.csv'
callsign = 'W1BUR'
freq = [3,7] # 3, 7 [MHz]

try:
    for f in freq:
        plotwspr(dat,callsign, f)
except NameError:
    dat = readwspr(csvfn, callsign, freq)
    for f in freq:
        plotwspr(dat,callsign,f)


show()