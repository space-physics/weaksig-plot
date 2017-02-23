from pathlib import Path
from datetime import datetime
from pytz import timezone
from numpy import in1d
from pandas import read_csv,DataFrame,cut
from matplotlib.pyplot import figure
import seaborn as sns


def readwspr(csvfn, callsign:str, band:int) -> DataFrame:
    csvfn = Path(csvfn).expanduser()
    callsign = callsign.upper()

    dat = read_csv(csvfn,
                   index_col=False,
                   usecols=[1,2,4,6,8,10,11,12,14],
                   names=['tut','rxcall','snr','txcall','power','distkm','az','band','code'],
                   #nrows=1000)
    )

    i = in1d(dat['band'],band) & ((dat['rxcall'] == callsign) | (dat['txcall'] == callsign))

    dat = dat.loc[i,:]

    return dat

def wsprstrip(dat, callsign:str, band:int):
    """
    due to low sample number, show point for each sample.
    horizontal jitter of points is random and just for plotting ease.
    """
    dat = dat.loc[dat['band']==band,:]

    bins = [0,50,100,250,500]

    cats = cut(dat['distkm'], bins)
    #dat['range_bins'] = cats
    dat,hcats = cathour(dat)

    ax = figure().gca()

    sns.swarmplot(x=cats,y='snr', hue=hcats, data=dat, ax=ax)
    ax.set_title(f'SNR [dB] vs. distance [km] for {callsign} on {band} MHz')

def plottime(dat,callsign,band):
    # list of stations that heard me or that I heard
    allcalls = dat['rxcall'].append(dat['txcall']).unique()

    for c in allcalls:
        if c == callsign: # I can't transmit or receive myself
            continue

        cdat = dat.loc[((dat['rxcall']==c) | (dat['txcall']==c)) & (dat['band'] == band), ['tut','distkm','snr']]
        if cdat.size==0:
            return

        distkm = cdat['distkm'].iat[0] # NOTE: assumes not moving
        if cdat.shape[0] < 3 or distkm>250: # if not many data points, skip plotting, or if too far for NVIS
            continue

        cdat, hcats = cathour(cdat)

        ax = figure().gca()
        sns.stripplot(x=hcats,y='snr',data=cdat,jitter=True,ax=ax)
        ax.set_title(f'SNR [dB] vs. time [local] for {c} on {band} MHz, distance {distkm} km.' )

def cathour(dat):
    dat['t'] = [datetime.utcfromtimestamp(u).astimezone(timezone('US/Eastern')) for u in dat['tut']]
    dat['hod'] = [r.hour for r in dat.t]
    bins = range(0,24+3,3) # hours of day
    cats = cut(dat['hod'],bins)

    return dat,cats