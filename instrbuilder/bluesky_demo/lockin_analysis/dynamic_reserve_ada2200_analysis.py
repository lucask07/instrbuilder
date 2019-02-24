import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from databroker import Broker
from plot_configs import params, dpi, figure_dir

rcParams.update(params)
SAVE_FIGS = False

db = Broker.named('local_file')  # a broker poses queries for saved data sets)

uid_baseline = 'cb4388b4-92ab-4eb3-bba1-8d44fa5cc138'
uid = '470bc279-b9bc-4c99-9a50-c4e949596cd5'

baseline = db[uid_baseline].table()
mean_baseline = np.mean(baseline['filter_6dB_mean'])
print('Baseline measurement = {}'.format(mean_baseline))

header = db[uid]  # db is a DataBroker instance
df = header.table()

# determine signal amplitude
sig_att = header['start']['attenuator_RCLK'].replace('dB', '')  # units of dB, strip of units
sig_amp = 2.71  # V-pkpk measured after the diff amp
sig_amp = sig_amp*10**(-float(sig_att)/20.0)  # input signal in pk-pk

# interferer amplitude
int_att = header['start']['attenuator_fg2'].replace('dB', '')  # units of dB, strip of units
int_amp_mult = 10**(-float(int_att)/20.0)*0.5   # FG signal multiplier (x0.5 due to amplifier is 1/2 V/V)

# center frequency (RCLK output)
fc = 390.58

# store data
x = []
y = []

percent_error = 5

for f in df['fg_freq'].unique():
    idx = (df['fg_freq'] == f)

    if np.abs((mean_baseline - df.loc[idx]['filter_6dB_mean'].iloc[-1]))/mean_baseline*100 > percent_error:
        print('Did not find value at f = {} [Hz]'.format(f))

    else:
        x.append(f)
        y.append(df.loc[idx]['fg_v'].iloc[-1])

plt.figure(dpi=160)
plt.semilogx(np.asarray(x), 20*np.log10(int_amp_mult*np.asarray(y)/sig_amp),
             marker='*', color='k')
plt.axvline(x=fc, color='k', linestyle='--', LineWidth=0.5)
plt.grid(True)
plt.ylabel('Interferer Rejection [dB]')
plt.xlabel('Freq [Hz]')
plt.grid(True)
if SAVE_FIGS:
	plt.savefig(os.path.join(figure_dir, 'dynamic_reserve_ADA2200.eps'))
plt.show()
