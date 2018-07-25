import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
from databroker import Broker
from scipy.interpolate import splev, splrep

figure_dir = '/Users/koer2434/Google Drive/UST/research/bluesky/manuscript/bluesky_manuscript/figures/'
params = {
   'axes.labelsize': 8,
   'font.size': 8,
   'legend.fontsize': 8,
   'xtick.labelsize': 10,
   'ytick.labelsize': 10,
   'text.usetex': True,
   'figure.figsize': [4.5, 4.5]
   }
rcParams.update(params)

db = Broker.named('local_file')  # a broker poses queries for saved data sets)
uid_baseline = 'b49db554-836e-4d39-80bd-22b406680c12'
uid = 'b3c25a50-84f2-4c6c-a845-61b64f9332b4'

baseline = db[uid_baseline].table()
expected_value = np.mean(baseline['lockin_A'])

header = db[uid]  # db is a DataBroker instance
df = header.table()
plt.figure(dpi=120)

x = []
y = []

# add a dashed line at the center frequency
# add collection around fc/2, fc/3, 3fc
# semilog? 


for int_v in df['fgen2_freq'].unique():
    idx = (df['fgen2_freq'] == int_v)
    x.append(int_v)
    y.append(df.loc[idx]['fgen2_v'].iloc[-1])
plt.semilogx(np.asarray(x), np.asarray(y), marker='*')
plt.grid(True)
plt.show()