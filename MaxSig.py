#!/usr/bin/env python
"""
http://wsprnet.org/drupal/downloads

Processes and plot gigabyte .csv files containing WSPR propagation data

Examples:
./MaxSig.py w1bur ~/data/wsprspots-2017-02.tsv --c2 kk1d wa9wtk w2grk k3rwr -b 7 -t 2017-02-27T23 2018-01-01T00

./MaxSig.py w1bur ~/data/wsprspots-2017-02.tsv --c2 kk1d wa9wtk -b 3

./MaxSig.py w1bur data/wspr-w1bur-2017-03-01.h5

"""
from pandas import DataFrame
from matplotlib.pyplot import show
#
from weaksig_plot import readwspr
from weaksig_plot.plots import wsprstrip,plottime

#fn = 'data/wsprspots-2017-02.csv'
#fn = 'data/2017-02-23.tsv'

def wsprplots(dat:DataFrame, callsign:str, call2:str, band:int, maxcalls:int, outfn, verbose:bool):
    for b in band:
#        wsprstrip(dat,callsign, b)

        plottime(dat,callsign, b, call2, outfn, verbose)

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='WSPR weak signal SNR/Hz/Watt plotter')
    p.add_argument('callsign',help='callsign of interest (case insensitive)')
    p.add_argument('fn',help='directory or list of .csv or .tsv files to plot')
    p.add_argument('--c2',help='second callsign(s) to plot to/from',nargs='+')
    p.add_argument('-b','--band',help='frequency band (integer MHz) to plot [3,5,7]',nargs='+',default=[3,5,7],type=int)
    p.add_argument('--maxcalls',help='if more than this number of stations, do not do individual time plots to save time',type=int,default=10)
    p.add_argument('-t','--tlim',help='start stop time limites to plot',nargs=2)
    p.add_argument('-v','--verbose',action='store_true')
    p.add_argument('-o','--outfn',help='hdf5 file to dump plotted data to',default='')
    p = p.parse_args()

#    try: # save time by reusing already loaded data
#        if dat.shape[0]==0: # bad read, try again
#            del dat
#        wsprplots(dat, p.callsign, p.c2, p.band, p.maxcalls, p.outfn, p.verbose)
#    except NameError: # load then plot
    dat = readwspr(p.fn, p.callsign, p.band, p.c2, p.tlim)
    wsprplots(dat, p.callsign, p.c2, p.band, p.maxcalls, p.outfn, p.verbose)

    show()
