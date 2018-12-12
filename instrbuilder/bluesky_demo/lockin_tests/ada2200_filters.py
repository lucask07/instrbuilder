# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

"""
Sandbox for testing scipy filters that act on arrays of data from bluesky
"""

import os
# imports that may need installation
import scipy.signal as signal
import numpy as np
import matplotlib.pyplot as plt
from databroker import Broker
from matplotlib import rcParams
from plot_configs import params, dpi, figure_dir

rcParams.update(params)

def create_filter(order, sample_rate, tau):
    cutoff_freq = 1 / (2 * np.pi * tau)
    norm_cutoff_freq = cutoff_freq / (sample_rate / 2)  # [from 0 - 1]

    num, denom = signal.iirfilter(N=order, Wn=norm_cutoff_freq,
                            rp=None, rs=None, btype='lowpass', analog=False,
                            ftype='butter', output='ba')
    return num, denom


def apply_filter(arr, num, denom, sample_rate, tau):

    output_signal = signal.filtfilt(num, denom, arr)

    tau_settle = 5
    settle_idx = int(tau_settle*tau/(1/sample_rate))
    decimate_length = int(tau/(1/sample_rate))

    # arr_downsample = signal.decimate(output_signal[settle_idx:], decimate_length)
    arr_downsample = output_signal[settle_idx::decimate_length]

    return arr_downsample[0], arr_downsample

plt.figure(dpi=300)

db = Broker.named('local_file')  # a broker poses queries for saved data sets)
data_dir = db.get_config()['metadatastore']['directory']

# get data into a pandas data-frame
uid = 'b270dad3-96fd-475a-ad1e-b2789db96ed0'
header = db[uid]
print(header.table())
df = header.table()

filename = os.path.join(data_dir, df['dmm_burst_volt_timer'][8])
arr = np.load(filename)

order = 4  # db/octave = order*6dB
sample_rate = 1220.680518480077*8  # 5e6/512/8*8 Hz
print('Sample rate = {} [Hz]'.format(sample_rate))
tau = 30e-3
cutoff_freq = 1/(2*np.pi*tau)
norm_cutoff_freq = cutoff_freq/(sample_rate/2)  # [from 0 - 1]

b, a = signal.iirfilter(N = order, Wn = norm_cutoff_freq,
	                    rp=None, rs=None, btype='lowpass', analog=False,
	                    ftype='butter', output='ba')

w, h = signal.freqz(b, a, 10000)
fig = plt.figure()
ax = fig.add_subplot(111)
ax.semilogx(w, 20 * np.log10(abs(h*(1))), marker='x')

plt.figure()
plt.plot(arr, marker='x')
# timeit: 107 us with array of 1024
output_signal = signal.filtfilt(b, a, arr)
plt.plot(output_signal, marker='o')

# timeit: 142 us with array of 4096
# l = np.concatenate((arr,arr,arr,arr))
# output_signal = signal.filtfilt(b, a, l)

print('Total data time = {} [s]'.format(len(arr)*1/sample_rate))
print('Total data time = {} [Tau]'.format(len(arr)*1/sample_rate/tau))

num, denom = create_filter(order, sample_rate, tau)
val, arr_downsample = apply_filter(arr, num, denom, sample_rate, tau)

