from pathlib import Path
from datetime import datetime
from dateutil.parser import parse
from numpy import in1d, log10,zeros, column_stack
from xarray import DataArray
from pandas import read_csv,DataFrame
import h5py
#
from sciencedates import forceutc

refbw = 2500 #[Hz] for WSPR
refdbm = 30 # [dBm] makes SNR/W
MAXNVISDIST=250 # [km] arbitrary maximum distance to be considered NVIS for plotting time
MINPOINTS = 3 # minimum number of station measurements to be time plotted

def readwspr(fn, callsign:str, band:int, call2, tlim) -> DataFrame:
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
                   usecols=[0,1,2,3,5,6,8,9,10],
                   names=['t','txcall','band','snr','txgrid','power','rxcall','rxgrid','distkm'],
                   dtype={'t':str,'txcall':str,'band':float,'snr':int,'txgrid':str,'power':int,
                          'rxcall':str,'rxgrid':str,'distkm':int},
                   #nrows=1000)
            )
#%% sanitization
            dat['band'] = dat['band'].astype(int)
            dat['t'] = [forceutc(datetime.strptime(t.strip(),'%Y-%m-%d %H:%M')) for t in dat['t']]
            dat['rxcall'] = dat['rxcall'].str.strip()
            dat['txcall'] = dat['txcall'].str.strip()
    elif fn.suffix=='.h5': #assume preprocessed data
        """
        here we assume the hierarchy is by callsign
        """
        dat = {}
        with h5py.File(str(fn),'r',libver='latest') as f:
            for c in f['/']: # iterate over callsign
                dat[c] = DataFrame(index=f[f'{c}/t'],
                                   columns=['snr','band'],
                                   data=column_stack(f[f'{c}/snr'],f[f'{c}/band']))
    else:
        raise ValueError(f'{fn} is not a known type to this program')

    print(f'done loading {fn}')
#%% extract only data relevant to our callsign on selected bands
    i = in1d(dat['band'],band) & ((dat['rxcall'] == callsign) | (dat['txcall'] == callsign))

    if call2 is not None:
        i &= in1d(dat['rxcall'],call2)

    if tlim is not None:
        tlim = [forceutc(parse(t)) for t in tlim]
        i &= (dat.t >= tlim[0]) & (dat.t <= tlim[1])

    dat = dat.loc[i,:]
#%% sanitize multiple reports in same minute
    print('cleaning data')
    dat = cleandistortion(dat,call2)
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

    N = dat.shape[0]

    invalid = zeros(N, dtype=bool)
    for k,t in enumerate(dat.t.unique()): # for each time step...
        if N>1000 and not k % 20:
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




