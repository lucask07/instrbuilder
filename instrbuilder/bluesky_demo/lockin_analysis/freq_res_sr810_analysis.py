# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

'''
analysis of SR810 frequency resolution
paper Figure 3
'''
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
from databroker import Broker
from scipy.interpolate import splev, splrep

from plot_configs import params, dpi, figure_dir
from metadata_parsing import print_meta

rcParams.update(params)

SAVE_FIGS = False
SHOW_FIT = False

try:
    db
except NameError:
    db = Broker.named('local_file')

uid = '3de221b4-b9d5-470f-a2b8-a9c3e09a6e94'
print('UID = {}'.format(uid[0:6]))
header = db[uid]  # db is a DataBroker instance
df = header.table()

plt.figure(dpi=dpi)
for fs in df['srs_lockin_filt_slope'].unique():
    idx = (df['srs_lockin_filt_slope'] == fs)
    plt.semilogy(df.loc[idx]['fg_freq'], df.loc[idx]['amp'],
                 marker='*',
                 label='Filter = {}'.format(fs.replace('-', ' ')))

plt.grid(True)
plt.legend()
plt.ylabel('A [V RMS]')
plt.xlabel('f [Hz]')
if SAVE_FIGS:
    plt.savefig(os.path.join(figure_dir, 'freq_res_sr810.eps'))

# ----------- analyze the data ------

# get instrument parameters from the metadata! No need to refer to a lab notebook.
fref = header['start']['lia_config']['srs_lockin_freq']['value']  # lock-in reference frequency
tau = header['start']['lia_config']['srs_lockin_tau']['value']  # lock-in time-constant
fc = 1/(2*np.pi*tau)  # find the filter cutoff frequency

for fs in df['srs_lockin_filt_slope'].unique():
    idx = (df['srs_lockin_filt_slope'] == fs)
    x = df.loc[idx]['fg_freq']
    y = df.loc[idx]['amp']

    # find peak amplitude and freq. of peak amplitude at frequency close to fref
    f_search = np.linspace(fref - 6, fref + 6, num=10000)

    spl = splrep(x, y)
    val_int = splev(f_search, spl)
    if SHOW_FIT:
        plt.plot(f_search, val_int, marker='o')

    amp_fref = np.max(val_int)
    max_f = f_search[np.where(val_int == amp_fref)][0]

    print('At filter-slope of {}; peak amplitude of {:.3f} at {:.3f} Hz'.format(fs, amp_fref, max_f))

    for octave in [0, 1, 2, 3]:
        # find amplitude at a number of octaves beyond cutoff frequency
        amp_fref_oct = np.asscalar(splev(max_f + 2**octave*fc, spl))
        # find amplitude 2 octaves beyond cutoff frequency
        # print result, 1 octave; 2 octaves
        print('{} octave past cutoff {:.3f}; attenuation = {:.3f} dB'.format(octave,
                                                                     amp_fref_oct, 20*np.log10(amp_fref_oct/amp_fref)))
# --------- metadata -----------------
print_meta(header, os.path.basename(__file__))

'''
import datetime
# start of the experiment: header['start']
# end of the experiment: header['stop']
print('-'*70)
print('METADATA')
print('-'*70)

print('Parsing metadata for UID: {}; with exit status: {}'.format(header.start['uid'], header.stop['exit_status']))

# time of experiment
print('Experiment start time: {}'.format(datetime.datetime.fromtimestamp(header.start['time']).strftime('%Y-%m-%d %H:%M:%S') ))
# experiment duration
print('Experiment duration: {} [seconds]'.format(header.stop['time'] - header.start['time']))

# Bluesky plan info 
print('Bluesky plan type: {} '.format(header.start['plan_type']))
print('Bluesky plan name: {} '.format(header.start['plan_name']))

# number of FG configuration keys
print('Metadata has {} stored function generator configuration values'.format(len(list(header.start['fg_config']))))

# example Function generator configuration values 
print('Example FG config values:')
for cfg_key in ['fg_function', 'fg_freq', 'fg_v', 'fg_offset', 'fg_load']:
    print('  Config value: {} = {}'.format(cfg_key, header.start['fg_config'][cfg_key]['value']))

# number of lock-in amplifier configuration keys
print('Metadata has {} stored lock-in configuration values'.format(len(list(header.start['lia_config']))))
print('Example lock-in config values:')
for cfg_key in ['srs_lockin_freq', 'srs_lockin_tau', 'srs_lockin_in_config', 'srs_lockin_sensitivity']:
    print('  Config value: {} = {}'.format(cfg_key, header.start['lia_config'][cfg_key]['value']))

'''

plt.show()
