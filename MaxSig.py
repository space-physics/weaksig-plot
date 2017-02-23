#!/usr/bin/env python
"""
http://wsprnet.org/drupal/downloads
"""
from matplotlib.pyplot import show
#
from weaksig_plot import readwspr, wsprstrip,plottime

csvfn = 'data/wsprspots-2017-02.csv'
callsign = 'W1BUR'
freq = [3,7] # 3, 7 [MHz]

def wsprplots(dat,callsign,freq):
    for f in freq:
        wsprstrip(dat,callsign, f)

    plottime(dat,callsign,freq[1])

if __name__ == '__main__':
    try:
        wsprplots(dat,callsign,freq)
    except NameError:
        dat = readwspr(csvfn, callsign, freq)
        wsprplots(dat,callsign,freq)

    show()