# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports
import os

# imports that may need installation
import matplotlib.pyplot as plt
from matplotlib import rcParams
from databroker import Broker

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

db = Broker.named('local_file')  # a broker poses queries for saved data sets)

# get data into a pandas data-frame
uid = 'cfc03b49-ea19-4745-b26d-5494fd3962e8'
header = db[uid]
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
df_meta = header.table('baseline')

print('These configuration values are saved to baseline data:')
print(df_meta.columns.values)

# This works, however the phase does drift slightly
offset = 3.3/2
plt.plot(df['fgen_phase'], df['dmm_burst_volt_timer_mean'] - offset, marker='*')
plt.xlabel('Phase [deg]')
plt.ylabel('Magnitude [V]')
plt.grid(True)
plt.savefig(os.path.join(figure_dir, 'phase_res_ada2200.eps'))
