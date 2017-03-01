from pathlib import Path
from datetime import datetime
from pytz import timezone
from numpy import in1d, log10,zeros
from xarray import DataArray
from pandas import read_csv,DataFrame,cut
from matplotlib.pyplot import figure
import seaborn as sns
#
from sciencedates import forceutc

refbw = 2500 #[Hz] for WSPR
refdbm = 30 # [dBm] makes SNR/W
MAXNVISDIST=250 # [km] arbitrary maximum distance to be considered NVIS for plotting time
MINPOINTS = 3 # minimum number of station measurements to be time plotted
TIMEZONE = 'US/Eastern' # TODO make parameter

def readwspr(fn, callsign:str, band:int, call2) -> DataFrame:
    fn = Path(fn).expanduser()
    callsign = callsign.upper()
    if isinstance(call2,(tuple,list)):
        call2=[c.upper() for c in call2]

    if fn.suffix == '.csv': # .gz not readable for some reason
            dat = read_csv(fn,
                   sep=',',
                   index_col=False,
                   usecols=[1,2,4,6,8,10,11,12,14],
                   names=['tut','rxcall','snr','txcall','power','distkm','az','band','code'],
                   dtype={'tut':int,'rxcall':str,'snr':int,'txcall':str,'power':int,
                          'distkm':int,'az':int,'band':int,'code':int},
                   #nrows=1000)
                   memory_map=True,
                   )
            dat['t'] = [forceutc(datetime.utcfromtimestamp(u)) for u in dat['tut']]
    elif fn.suffix=='.tsv':
            dat = read_csv(fn,
                   sep='\t',
                   index_col=False,
                   usecols=[0,1,2,3,6,8,10],
                   names=['t','txcall','band','snr','power','rxcall','distkm'],
                   dtype={'t':str,'txcall':str,'band':float,'snr':int,'power':int,
                          'rxcall':str,'distkm':int},
                   #nrows=1000)
            )
#%% sanitization
            dat['band'] = dat['band'].astype(int)
            dat['t'] = [forceutc(datetime.strptime(t.strip(),'%Y-%m-%d %H:%M')) for t in dat['t']]
            dat['rxcall'] = dat['rxcall'].str.strip()
            dat['txcall'] = dat['txcall'].str.strip()
    else:
        raise ValueError(f'{fn} is not a known type to this program')

    print(f'done loading {fn}')
#%% extract only data relevant to our callsign on selected bands
    i = in1d(dat['band'],band) & ((dat['rxcall'] == callsign) | (dat['txcall'] == callsign))
    if call2 is not None:
        i &= in1d(dat['rxcall'],call2)

    dat = dat.loc[i,:]
#%% sanitize multiple reports in same minute
    print('cleaning data')
    dat = cleandistortion(dat,call2)
    print('done cleaning data')
#%% compensate SNR -> SNR/Hz/W
    dat['snr'] += round(10*log10(refbw)) # snr/Hz

    dat['snr'] += refdbm - dat['power'] # snr/Hz/W

    return dat

def cleandistortion(dat:DataArray,call2:list=None):
    """
    unless you're running multiple transmitters or receivers, you shouldn't see multiple
    signal reports in the same minute from/to the same station.
    These multiple reports can happen due to distortion in the receiver or transmitter.

    This is improvised method, due to few NVIS stations to measure.

    right now we clean distortion only in others' receivers.
    """
    if call2 is None:
        rxcalls = dat.loc['rxcall'].unique()
    else:
        rxcalls = call2

    invalid = zeros(dat.shape[0], dtype=bool)
    for k,t in enumerate(dat.t.unique()): # for each time step...
        if not k % 20:
            print(t)

        i = dat.t == t # boolean
        if i.sum() == 1:
            continue # can't be dupe if there's only one report at this time!

        for c in rxcalls:
            j = i & (dat.rxcall == c)
            if j.sum() <= 1:
                continue # normal case, 0 or 1 spot by this call

            ok = dat.loc[j,'snr'].argmax()
            j[ok] = False
            invalid |= j

    dat = dat.loc[~invalid,:] # this is OK because of Pandas index referring to original indices

    return dat




def wsprstrip(dat:DataFrame, callsign:str, band:int):
    """
    due to low sample number, show point for each sample.
    horizontal jitter of points is random and just for plotting ease.
    """
    callsign = callsign.upper()

    def _anno(ax):
        ax.set_title(f'SNR/Hz/W [dB] vs. distance [km] and time [local] for {callsign} on {band} MHz')
        ax.set_ylabel('SNR/Hz/W [dB]')

    dat = dat.loc[dat['band']==band,:]
    if dat.shape[0]==0: # none this band
        return

    bins = [0,20,50,100,250,500,1000,2500,5000,10000,41000]

    cats = cut(dat['distkm'], bins)
    #dat['range_bins'] = cats
    dat,hcats = cathour(dat, TIMEZONE)
#%% swarm
#    ax = figure().gca()
#    sns.swarmplot(x=cats,y='snr', hue=hcats, data=dat, ax=ax)
#    _anno(ax)
#%% box
    print('boxplot')
    ax = figure().gca()
    sns.boxplot(x=cats,y='snr', hue=hcats, data=dat, ax=ax)
    _anno(ax)
#%% violin
    #ax = figure().gca()
   # sns.violinplot(x=cats,y='snr',hue=hcats,data=dat,ax=ax)
   # _anno(ax)

def plottime(dat:DataFrame, callsign:str, band:int, call2:list=None):
    if not call2:
        return

    assert isinstance(call2,(tuple,list)),'list of calls received'
    call2=[c.upper() for c in call2]
    callsign=callsign.upper()

    dat = dat.loc[dat['band']==band,:]
    if dat.shape[0]==0: # none this band
        return
    # list of stations that heard me or that I heard
    #allcalls = dat['rxcall'].append(dat['txcall']).unique()

    cols = ['t','distkm','snr']

    cdat = dat.loc[(in1d(dat['rxcall'],call2) | in1d(dat['txcall'],call2)) & (dat['band'] == band), cols]
    if cdat.shape[0]==0:
        return

    distkm = cdat['distkm'].iat[0] # NOTE: assumes not moving

    cdat, hcats = cathour(cdat, TIMEZONE)
#%% swarm
    ax = figure().gca()
    sns.swarmplot(x=hcats,y='snr',hue=hcats,data=cdat,ax=ax)
    ax.set_title(f'SNR/Hz/W [dB] vs. time [local] for {call2} on {band} MHz, distance {distkm} km.' )
    ax.set_ylabel('SNR/Hz/W [dB]')
#%% box
    ax = figure().gca()
    sns.boxplot(x=hcats,y='snr',hue=hcats,data=cdat,ax=ax)
    ax.set_title(f'SNR/Hz/W [dB] vs. time [local] for {call2} on {band} MHz, distance {distkm} km.' )
    ax.set_ylabel('SNR/Hz/W [dB]')
#%%
    ax = figure().gca()
    ax.plot(cdat.t.values, cdat.snr.values, linestyle='-',marker='.')
    ax.set_xlabel('time [local]')
    ax.set_ylabel('SNR/Hz/W  [dB]')
    ax.set_title(f'SNR/Hz/W [dB] vs. time [local] for {call2} on {band} MHz, distance {distkm} km.' )


def cathour(dat, tz):
    # hour of day, local time
    dat['hod'] = [t.astimezone(timezone(tz)).hour for t in dat['t']]

    bins = range(0, 24+6, 6) # hours of day
    cats = cut(dat['hod'],bins)

    return dat, cats