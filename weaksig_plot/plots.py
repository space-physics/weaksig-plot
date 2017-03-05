from pathlib import Path
from pandas import DataFrame,cut
from pytz import timezone
from numpy import in1d,datetime64, timedelta64
from matplotlib.pyplot import figure
import seaborn as sns
import h5py


TIMEZONE = 'US/Eastern' # TODO make parameter


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
    hcats = cathour(dat, TIMEZONE)
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

def plottime(dat:DataFrame, callsign:str, band:int, call2:list=None, outfn:str='',verbose:bool=False):
    if not call2:
        return

    outfn = Path(outfn).expanduser()

    assert isinstance(call2,(tuple,list)),'list of calls received'
    call2=[c.upper() for c in call2]
    callsign=callsign.upper()

    dat = dat.loc[dat['band']==band,:]
    if dat.shape[0]==0: # none this band
        return
    # list of stations that heard me or that I heard
    #allcalls = dat['rxcall'].append(dat['txcall']).unique()

    cols = ['t','distkm','snr','rxcall','band']

    cdat = dat.loc[(in1d(dat['rxcall'],call2) | in1d(dat['txcall'],call2)) & (dat['band'] == band), cols]
    if cdat.shape[0]==0:
        return

    distkm = []; az = []
    for c in call2:
        i = cdat['rxcall'] == c
        if i.sum()==0:
            distkm.append(None)
            continue
        distkm.append(cdat.loc[i,'distkm'].iat[0]) # NOTE: assumes not moving
        if 'az' in cdat:
            az.append(cdat.loc[i,'az'].iat[0])

    if verbose:
      for j,c in enumerate(call2):
        i = cdat['rxcall'] == c
        D = cdat.loc[i,:]
        hcats = cathour(D, TIMEZONE)
#%% swarm
#        ax = figure().gca()
#        sns.swarmplot(x=hcats, y='snr',hue=hcats,data=D, ax=ax)
#        ax.set_title(f'SNR/Hz/W [dB] vs. time [local] for {c} on {band} MHz, distance {distkm} km.' )
#        ax.set_ylabel('SNR/Hz/W [dB]')
#%% box
        ax = figure().gca()
        sns.boxplot(x=hcats, y='snr',data=D, ax=ax)
        ax.set_title(f'SNR/Hz/W [dB] vs. time \n{c} on {band} MHz, distance {distkm[j]} km.' )
        ax.set_ylabel('SNR/Hz/W [dB]')
#%%
    if outfn:
        outfn = outfn.parent/(outfn.stem + f'_{band}.h5') # FIXME hack
        if outfn.is_file():
            outfn.unlink()
#%%
    ax = figure().gca()
    for j,c in enumerate(call2):
        i = cdat['rxcall'] == c
        if i.sum() == 0:
            continue
        D = cdat.loc[i,:]
        hcats = cathour(D, TIMEZONE)

        # store time as Unix timestamp
        if outfn:

            print(f'writing {outfn}')
            with h5py.File(str(outfn),'a',libver='latest') as f:
                f[f'/{c}/t'] = (D.t.values-datetime64('1970-01-01T00Z'))/timedelta64(1,'s')
                f[f'/{c}/snr'] = D.snr
                f[f'/{c}/band'] = D.band
                f[f'/{c}/distkm'] = distkm[j]
                if az:
                    f[f'/{c}/azimuth'] = az[j]

        ax.plot(D.t, D.snr, linestyle='-',marker='.',label=str(distkm[j]),markersize=10)
        ax.set_xlabel('time [UTC]')
        ax.set_ylabel('SNR/Hz/W  [dB]')

    ax.set_title(f'SNR/Hz/W [dB] vs. time \n{call2} on {band} MHz.' )
    ax.legend(title='distance [km]')

def cathour(dat, tz):
    # hour of day, local time
    hod = [t.astimezone(timezone(tz)).hour for t in dat.t]

    bins = range(0, 24+6, 6) # hours of day
    cats = cut(hod,bins)

    return cats
