import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from databroker import Broker
from plot_configs import params, dpi, figure_dir

rcParams.update(params)

db = Broker.named('local_file')  # a broker poses queries for saved data sets)
# uid_baseline = '6ed43246-6e65-4fbe-9b9b-29f7c24b5194' -> just harmonics
uid_baseline = 'd844e08d-1d5b-4203-9b58-3f685bb2e919'
uid_baseline = 'a4b267bf-cf35-42ed-90a4-ab443e856d26'
uid_baseline = '5854f857-ce1f-4bd2-972c-380672dec6ed'
uid_baseline = 'cb4388b4-92ab-4eb3-bba1-8d44fa5cc138'


# uid = 'f9d3b57d-f7dd-446c-bfff-96b691c415c1'
uid = '6454c5ca-505e-4844-b9f0-7cb153567321'
uid = '09bf1368-3ff4-4272-913f-40133cf95f5a'
uid = '03a6cf4d-11a1-476a-85d3-cf50c135a156'
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

# determine center frequency (RCLK output)
fc = 390.58

# store data
x = []
y = []

# revisit the definition of dynamic reserve. Should my signal be within 10% of full-scale?

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
plt.savefig(os.path.join(figure_dir, 'dynamic_reserve_ADA2200.eps'))
plt.show()
