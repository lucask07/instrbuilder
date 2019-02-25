# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports
import os

# imports that may need installation
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from databroker import Broker
from plot_configs import params, dpi, figure_dir
from metadata_parsing import print_meta

rcParams.update(params)
plt.figure(dpi=dpi)

try:
    db
except NameError:
    db = Broker.named('local_file') # a broker poses queries for saved data sets

'''
|  0 | f31271f1-4231-4798-afe6-83e8647c0927 | 2018-07-06 15:29:07 | phase_dependence_offset | count       | ADA2200 |           10 |
|  1 | 63bfefd6-3cc6-45ef-9497-2e97a5cf8f6f | 2018-07-06 15:28:36 | phase_dependence_offset | count       | ADA2200 |           10 |
|  2 | b270dad3-96fd-475a-ad1e-b2789db96ed0 | 2018-07-06 15:27:07 | phase_dependence        | scan        | ADA2200 |           60 |
'''

# get data into a pandas data-frame
uid = '8a24caa4-8a72-454b-ae0b-4dfd71b7751d'
header = db[uid]  # db is a DataBroker instance
print('UID = {}'.format(uid[0:6]))

print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
h = db[-1]
df_meta = h.table('baseline')
print_meta(header, os.path.basename(__file__))

phase_diff = np.array([])

for f in df['fgen_freq'].unique():
    idx = df.index[df['fgen_freq'] == f].tolist()
    time_diff = (df['time'][idx[0]].to_pydatetime() - df['time'][idx[-1]].to_pydatetime()).total_seconds()
    total_diff = (df['osc_meas_phase'][idx[0]] - df['osc_meas_phase'][idx[-1]])/time_diff
    phase_diff = np.append(phase_diff, total_diff)

plt.plot(df['fgen_freq'].unique(), phase_diff, marker='*')
plt.ylabel('Degree/second')
plt.xlabel('Freq [Hz]')
plt.grid(True)
if SAVE_FIGS:
	plt.savefig(os.path.join(figure_dir, 'phase_tuning_ada2200.eps'))
plt.show()

import scipy.interpolate
y_interp = scipy.interpolate.interp1d(phase_diff, df['fgen_freq'].unique())
optimal_freq = y_interp(0)
print('Frequency of minimum phase drift = {} [Hz]'.format(optimal_freq))
