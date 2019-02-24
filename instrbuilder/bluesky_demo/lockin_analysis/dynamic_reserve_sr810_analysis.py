import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from databroker import Broker
from plot_configs import params, dpi, figure_dir
rcParams.update(params)

SAVE_FIGS = False

db = Broker.named('local_file')  # a broker poses queries for saved data sets)
uid_baseline = '8e3f2f50-a302-4442-ba50-ff4f4b58fdf2'
uid = 'ffcd20b8-f7ca-4d90-9534-e68e68237156'

baseline = db[uid_baseline].table()
mean_baseline = np.mean(baseline['lockin_A'])
print('Baseline measurement = {}'.format(mean_baseline))

header = db[uid]  # db is a DataBroker instance
df = header.table()

# determine signal amplitude
sig_att = header['start']['attenuator_fg1'].replace('dB', '')  # units of dB, strip of units
sig_amp = header['start']['fg_config']['fgen_v']['value']
sig_amp = 2*sig_amp*10**(-float(sig_att)/20.0) / (2*np.sqrt(2))  # FG in pk-pk, convert to RMS

# interferer amplitude
int_att = header['start']['attenuator_fg2'].replace('dB', '')  # units of dB, strip of units
int_amp_mult = 2*10**(-float(int_att)/20.0) / (2*np.sqrt(2))  # FG in pk-pk, convert to RMS

# determine center frequency (signal function generator frequency)
fc = header['start']['fg_config']['fgen_freq']['value']

# summarize critical lock-in parameters
for config_name in ['tau', 'res_mode', 'sensitivity']:  # 'filt_slope'
    print('{} = {}'.format(config_name,
                           header['start']['lia_config']['lockin_{}'.format(config_name)]['value']))

# store data
x = []
y = []

percent_error = 5
for f in df['fgen2_freq'].unique():
    idx = (df['fgen2_freq'] == f)

    if np.abs((mean_baseline - df.loc[idx]['lockin_A'].iloc[-1]))/mean_baseline*100 > percent_error:
        print('Did not find value at f = {} [Hz]'.format(f))

    else:
        x.append(f)
        y.append(df.loc[idx]['fgen2_v'].iloc[-1])

plt.figure(dpi=160)
plt.semilogx(np.asarray(x), 20*np.log10(int_amp_mult*np.asarray(y)/sig_amp),
             marker='*', color='k')
plt.axvline(x=fc, color='k', linestyle='--', LineWidth=0.5)
plt.grid(True)
plt.ylabel('Dynamic Reserve [dB]')
plt.xlabel('Freq [Hz]')
plt.grid(True)
if SAVE_FIGS:
	plt.savefig(os.path.join(figure_dir, 'dynamic_reserve_SR810.eps'))
plt.show()
