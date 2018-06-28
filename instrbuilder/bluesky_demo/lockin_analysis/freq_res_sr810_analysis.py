import os
import matplotlib.pyplot as plt
from matplotlib import rcParams

figure_dir = '/Users/koer2434/Google Drive/UST/research/bluesky/manuscript/bluesky_manuscript/figures/'
params = {
   'axes.labelsize': 8,
   'font.size': 8,
   'legend.fontsize': 10,
   'xtick.labelsize': 10,
   'ytick.labelsize': 10,
   'text.usetex': True,
   'figure.figsize': [4.5, 4.5]
   }
rcParams.update(params)


plt.figure(dpi=300)
for fs in df['lockin_filt_slope'].unique():
    idx = (df['lockin_filt_slope'] == fs)
    plt.semilogy(df.loc[idx]['fgen_freq'], df.loc[idx]['lockin_disp_val'],
                 marker='*',
                 label='Filt. slope = {}'.format(fs))
plt.grid(True)
plt.legend()
plt.ylabel('R [V RMS]')
plt.xlabel('f [Hz]')
plt.savefig(os.path.join(figure_dir, 'freq_res_sr810.eps'))
# metadata
header['start']
header['stop']

# view the baseline data (i.e. configuration values)
h = db[-1]
h.table('baseline')