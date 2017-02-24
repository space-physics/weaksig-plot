from pathlib import Path
from datetime import datetime
from pytz import timezone
from numpy import in1d, log10
from pandas import read_csv,DataFrame,cut
from matplotlib.pyplot import figure
import seaborn as sns

refbw = 2500 #[Hz] for WSPR
refdbm = 30 # [dBm] makes SNR/W
MAXNVISDIST=250 # [km] arbitrary maximum distance to be considered NVIS for plotting time
MINPOINTS = 3 # minimum number of station measurements to be time plotted

def readwspr(fn, callsign:str, band:int) -> DataFrame:
    fn = Path(fn).expanduser()
    callsign = callsign.upper()

    if fn.suffix=='.csv':
            dat = read_csv(fn,
                   sep=',',
                   index_col=False,
                   usecols=[1,2,4,6,8,10,11,12,14],
                   names=['tut','rxcall','snr','txcall','power','distkm','az','band','code'],
                   #nrows=1000)
                   )
    elif fn.suffix=='.tsv':
            dat = read_csv(fn,
                   sep='\t',
                   index_col=False,
                   usecols=[0,1,2,3,6,8,10],
                   names=['t','txcall','band','snr','power','rxcall','distkm'],
                   #nrows=1000)
            )

            dat['band'] = dat['band'].astype(int)
            dat['t'] = [datetime.strptime(t.strip(),'%Y-%m-%d %H:%M') for t in dat['t']]
            dat['rxcall'] = dat['rxcall'].str.strip()
            dat['txcall'] = dat['txcall'].str.strip()

    i = in1d(dat['band'],band) & ((dat['rxcall'] == callsign) | (dat['txcall'] == callsign))

    dat = dat.loc[i,:]
#%% compensate SNR -> SNR/Hz/W
    dat['snr'] += round(10*log10(refbw)) # snr/Hz

    dat['snr'] += refdbm - dat['power'] # snr/Hz/W

    return dat

def wsprstrip(dat:DataFrame, callsign:str, band:int):
    """
    due to low sample number, show point for each sample.
    horizontal jitter of points is random and just for plotting ease.
    """
    def _anno(ax):
        ax.set_title(f'SNR/Hz/W [dB] vs. distance [km] and time [local] for {callsign} on {band} MHz')
        ax.set_ylabel('SNR/Hz/W [dB]')

    dat = dat.loc[dat['band']==band,:]
    if dat.shape[0]==0: # none this band
        return

    bins = [0,20,50,100,250,500,1000,2500,5000,10000,41000]

    cats = cut(dat['distkm'], bins)
    #dat['range_bins'] = cats
    dat,hcats = cathour(dat)
#%% swarm
    ax = figure().gca()
    sns.swarmplot(x=cats,y='snr', hue=hcats, data=dat, ax=ax)
    _anno(ax)
#%% box
    ax = figure().gca()
    sns.boxplot(x=cats,y='snr', hue=hcats, data=dat, ax=ax)
    _anno(ax)
#%% violin
    #ax = figure().gca()
   # sns.violinplot(x=cats,y='snr',hue=hcats,data=dat,ax=ax)
   # _anno(ax)

def plottime(dat:DataFrame, callsign:str, band:int, maxcalls:int):
    if dat.shape[0]==0:
        return
    # list of stations that heard me or that I heard
    allcalls = dat['rxcall'].append(dat['txcall']).unique()
    if allcalls.size > maxcalls:
        print(f'skipping individual station plots since number of stations > {maxcalls}')
        return

    for c in allcalls:
        if c == callsign: # I can't transmit or receive myself
            continue
        
        cols = ['distkm','snr']
        if 't' in dat:
            cols += 't'
        elif 'tut' in dat:
            cols += 'tut'
        else:
            raise RuntimeError('times not in data? was file parsed correctly?')
            

        cdat = dat.loc[((dat['rxcall']==c) | (dat['txcall']==c)) & (dat['band'] == band), cols]
        if cdat.shape[0]==0:
            return

        distkm = cdat['distkm'].iat[0] # NOTE: assumes not moving
        if cdat.shape[0] < MINPOINTS or distkm>MAXNVISDIST: # if not many data points, skip plotting, or if too far for NVIS
            continue

        cdat, hcats = cathour(cdat)
#%%
        ax = figure().gca()
        sns.swarmplot(x=hcats,y='snr',hue=hcats,data=cdat,ax=ax)
        ax.set_title(f'SNR/Hz/W [dB] vs. time [local] for {c} on {band} MHz, distance {distkm} km.' )
        ax.set_ylabel('SNR/Hz/W [dB]')
#%%

def cathour(dat):
    if not 't' in dat:
        dat['t'] = [datetime.utcfromtimestamp(u).astimezone(timezone('US/Eastern')) for u in dat['tut']]

    dat['hod'] = [r.hour for r in dat.t]
    bins = range(0,24+6,6) # hours of day
    cats = cut(dat['hod'],bins)

    return dat,cats