from pathlib import Path
from numpy import in1d
from pandas import read_csv,DataFrame,cut
import seaborn as sns
from matplotlib.pyplot import figure


def readwspr(csvfn, callsign:str, band:int) -> DataFrame:
    csvfn = Path(csvfn).expanduser()
    callsign = callsign.upper()

    dat = read_csv(csvfn,
                   index_col=False,
                   usecols=[1,2,4,6,8,10,11,12,14],
                   names=['tut','rxcall','snr','txcall','power','distkm','az','band','code'],
                   #nrows=1000)
    )

    i = in1d(dat['band'],band) & (dat['rxcall'] == callsign) | (dat['txcall'] == callsign)

    dat = dat.loc[i,:]

    return dat

def plotwspr(dat, callsign:str, band:int):
    dat = dat.loc[dat['band']==band,:]


    bins = [0,50,100,250,500]

    cats = cut(dat['distkm'], bins)
    dat['range_bins'] = cats

    ax = figure().gca()

#    sns.boxplot(x=cats,y='snr',data=dat)
    sns.stripplot(x=cats,y='snr',data=dat, jitter=True, ax=ax)
    ax.set_title(f'SNR vs. distance [km] for {callsign} on {band} MHz')
