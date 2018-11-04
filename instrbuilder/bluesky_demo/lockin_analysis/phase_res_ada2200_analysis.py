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

rcParams.update(params)
plt.figure(dpi=dpi)

db = Broker.named('local_file')  # a broker poses queries for saved data sets)

'''
|  0 | f31271f1-4231-4798-afe6-83e8647c0927 | 2018-07-06 15:29:07 | phase_dependence_offset | count       | ADA2200 |           10 |
|  1 | 63bfefd6-3cc6-45ef-9497-2e97a5cf8f6f | 2018-07-06 15:28:36 | phase_dependence_offset | count       | ADA2200 |           10 |
|  2 | b270dad3-96fd-475a-ad1e-b2789db96ed0 | 2018-07-06 15:27:07 | phase_dependence        | scan        | ADA2200 |           60 |
'''

# get data into a pandas data-frame
uid = 'b270dad3-96fd-475a-ad1e-b2789db96ed0'
header = db[uid]
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
df_meta = header.table('baseline')

print('These configuration values are saved to baseline data:')
print(df_meta.columns.values)

# Read-in offset data
uid = 'f31271f1-4231-4798-afe6-83e8647c0927'
df_offset = header.db[uid].table()

offset = np.mean(df_offset['dmm_meas_volt'])
print('Offset measured as: {} [V]'.format(offset))

plt.figure()
plt.plot(df['osc_meas_phase'], df['dmm_burst_volt_timer_mean'] - offset,
         marker='*', LineStyle='None', color='k')
plt.xlabel('Phase [deg]')
plt.ylabel('Magnitude [V]')
plt.grid(True)

plt.xlabel('Phase [deg]')
plt.ylabel('Magnitude [V]')
plt.grid(True)
plt.savefig(os.path.join(figure_dir, 'phase_res_ada2200.eps'))
