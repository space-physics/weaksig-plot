#!/usr/bin/env python
"""
http://wsprnet.org/drupal/downloads

Processes and plot gigabyte .csv files containing WSPR propagation data
"""
from pandas import DataFrame
from matplotlib.pyplot import show
#
from weaksig_plot import readwspr, wsprstrip,plottime

#fn = 'data/wsprspots-2017-02.csv'
#fn = 'data/2017-02-23.tsv'

def wsprplots(dat:DataFrame, callsign:str, band:int, maxcalls:int):
    for b in band:
        wsprstrip(dat,callsign, b)

        plottime(dat,callsign, b, maxcalls)

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='WSPR weak signal SNR/Hz/Watt plotter')
    p.add_argument('callsign',help='callsign of interest (case insensitive)')
    p.add_argument('fn',help='directory or list of .csv or .tsv files to plot')
    p.add_argument('-b','--band',help='frequency band (integer MHz) to plot [3,5,7]',nargs='+',default=[3,5,7],type=int)
    p.add_argument('--maxcalls',help='if more than this number of stations, do not do individual time plots to save time',type=int,default=10)
    p = p.parse_args()

    try: # save time by reusing already loaded data
        if dat.shape[0]==0: # bad read, try again
            del dat
        wsprplots(dat, p.callsign, p.band, p.maxcalls)
    except NameError: # load then plot
        dat = readwspr(p.fn, p.callsign, p.band)
        wsprplots(dat, p.callsign, p.band, p.maxcalls)

    show()