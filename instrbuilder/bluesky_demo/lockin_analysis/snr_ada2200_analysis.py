
# standard library imports
import os

# imports that may need installation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from databroker import Broker

from plot_configs import params, dpi, figure_dir

rcParams.update(params)
rcParams.update(params)

db = Broker.named('local_file')  # a broker poses queries for saved data sets

# get data into a pandas data-frame
uid = 'f6e88efb-11d9-4c24-9921-0de7e2c0fb36'
header = db[uid]
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
df_meta = header.table('start')

fig = plt.figure(dpi=dpi)
ax = fig.add_subplot(2, 1, 1)

signal_name = 'my_multi_burst_volt_timer_filter_24dB_mean'
noise_name = 'my_multi_burst_volt_timer_filter_24dB_std'

att = df['att_val']
offset_corrected_val = -(df[signal_name] - df[signal_name][len(att)])
val_std = df[noise_name]

ax.plot(att[0:(len(att) - 1)], offset_corrected_val[0:(len(att) - 1)], marker='x', color='k')
plt.grid(True)
ax.set(xlabel='Attenuation [dB]', ylabel='Out [V]')
ax.set_yscale('log')

ax2 = fig.add_subplot(2, 1, 2)
ax2.plot(att[0:(len(att) - 1)], val_std[0:(len(att) - 1)]*1000, marker='x', color='k')
ylims = ax2.get_ylim()
ax2.set_ylim(0, ylims[1])
ax2.set(xlabel='Attenuation. [dB]', ylabel='Noise [mV]')
plt.grid(True)

plt.tight_layout()
# plt.savefig(os.path.join(figure_dir, 'snr_ada2200.eps'))
# plt.savefig(os.path.join(figure_dir, 'snr_ada2200.png'))

snr = offset_corrected_val[0:(len(att) - 1)]/val_std[0:(len(att) - 1)]
snr_bits = np.log2(snr)
print(np.log2(snr))
input_signal = 2.71  # volts pk-pk at 0 attenuation
print('Noise (no input) = {} [mV]'.format(val_std[len(att)]*1000))

# 2.71V Pk-pk, 1.6205 V avg over N-cycles; AC RMS 1.233

header['start']['ada2200_config']
