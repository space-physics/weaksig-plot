#!/usr/bin/env python
"""
http://wsprnet.org/drupal/downloads

Processes and plot gigabyte .csv and .tsv files containing WSPR propagation data

Examples:
./MapSig.py w1bur ~/data/wsprspots-2017-02.tsv wa9wtk kk1d

"""
from math import cos,atan,atan2,sin,tau
from pandas import DataFrame
from matplotlib.pyplot import figure,show
from mpl_toolkits.basemap import Basemap
from geopy.distance import vincenty as vdist
from pymap3d.vreckon import vreckon
#
import mlocs
from weaksig_plot import readwspr

F2h = 250 # [km] altitude of F2 layer reflection point (maximum Ne)

def wsprmap(dat:DataFrame, callsign:str, call2:str, band:int, maxcalls:int, outfn, verbose:bool):
    for b in band:
        drawmap(dat,callsign,call2,b)

def drawmap(dat,callsign,call2,b):
    callsign = callsign.upper()
    call2 = [c.upper() for c in call2]

    maid0 = dat.loc[dat['txcall']==callsign,'txgrid'].iat[0].strip()
    ll0 = mlocs.toLoc(maid0)
#%%
    ax= figure().gca()
    m = Basemap(projection='merc',
              llcrnrlat=ll0[0]-5, urcrnrlat=ll0[0]+5,
              llcrnrlon=ll0[1]-10,urcrnrlon=ll0[1]+10,
              lat_ts=20,
              resolution='l')
    m.drawcoastlines()
    m.drawcountries()
    #m.drawmeridians(arange(0,360,30))
    #m.drawparallels(arange(-90,90,30))
#%% plot self
    x,y = m(ll0[1],ll0[0])
    m.plot(x,y,'o',color='limegreen',markersize=8,markerfacecolor='none')
#%% plot others
    station = DataFrame(index=call2,columns =['muf_fact','latlon','midlatlon'])
    for c in call2:
        rxgrid = dat.loc[dat['rxcall']==c,'rxgrid'].iat[0].strip()
        latlon = mlocs.toLoc(rxgrid)
        distkm = vdist(ll0,latlon).km
        az = (atan2(sin(latlon[1]-ll0[1])*cos(latlon[0]), cos(ll0[0])*sin(latlon[0])-sin(ll0[0])*cos(latlon[0])*cos(latlon[1]-ll0[1])) + tau) % tau
        aoi = atan(distkm/2/F2h)

        station.loc[c,'muf_fact'] = 1/cos(aoi)
        station.loc[c,'latlon'] = latlon
        station.loc[c,'midlatlon'] = vreckon(ll0[0],ll0[1],distkm/2,az)

        x,y = m(latlon[1], latlon[0])
        m.plot(x,y,'o',color='red',markersize=8,markerfacecolor='none')

    ax.set_title(f'WSPR {b} MHz')
#%% plot Ne bound
    for t in dat.t.unique():
        print(t)




if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='WSPR weak signal SNR/Hz/Watt plotter')
    p.add_argument('callsign',help='callsign of interest (case insensitive)')
    p.add_argument('fn',help='directory or list of .csv or .tsv files to plot')
    p.add_argument('c2',help='second callsign(s) to plot to/from',nargs='+')
    p.add_argument('-b','--band',help='frequency band (integer MHz) to plot [3,5,7]',nargs='+',default=[1,3,5,7,10],type=int)
    p.add_argument('--maxcalls',help='if more than this number of stations, do not do individual time plots to save time',type=int,default=10)
    p.add_argument('-t','--tlim',help='start stop time limites to plot',nargs=2)
    p.add_argument('-v','--verbose',action='store_true')
    p.add_argument('-o','--outfn',help='hdf5 file to dump plotted data to',default='')
    p = p.parse_args()

    dat = readwspr(p.fn, p.callsign, p.band, p.c2, p.tlim)
    wsprmap(dat, p.callsign, p.c2, p.band, p.maxcalls, p.outfn, p.verbose)

    show()
