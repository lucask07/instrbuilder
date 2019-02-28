# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas
'''
analysis of ADA2200 phase resolution
paper Figure 4
'''
# standard library imports
import os
# imports that may need installation
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import scipy.interpolate as inter
from databroker import Broker

from plot_configs import params, dpi, figure_dir
from metadata_parsing import print_meta

rcParams.update(params)
plt.figure(dpi=dpi)

SAVE_FIGS = False

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
uid = 'b270dad3-96fd-475a-ad1e-b2789db96ed0'
print('UID = {}'.format(uid[0:6]))
header = db[uid]
df = header.table()
print_meta(header, os.path.basename(__file__))

# view the baseline data (i.e. configuration values)
print('open meta table')
df_meta = header.table('baseline')
print('These configuration values are saved to baseline data:')
print(df_meta.columns.values)

# Read offset data
uid_offset = 'f31271f1-4231-4798-afe6-83e8647c0927'
print('UID offset = {}'.format(uid_offset[0:6]))
print('offset table')
df_offset = header.db[uid_offset].table()

offset = np.mean(df_offset['dmm_meas_volt'])
print('Offset measured as: {} [V]'.format(offset))

plt.plot(df['osc_meas_phase'], df['dmm_burst_volt_timer_mean'] - offset,
         marker='*', LineStyle='None', color='k')
plt.xlabel('Phase [deg]')
plt.ylabel('Magnitude [V]')
plt.grid(True)

plt.xlabel('Phase [deg]')
plt.ylabel('Magnitude [V]')
plt.grid(True)

if SAVE_FIGS:
	plt.savefig(os.path.join(figure_dir, 'phase_res_ada2200.eps'))
plt.show()

# create a fit to the data to extrapolate:
	#1) the phase of the zero-crossing 
	#2) the conversion gain at the peak 
x = df['osc_meas_phase']
x_sort = np.sort(df['osc_meas_phase'])
x_idx = np.argsort(df['osc_meas_phase'])
x_fit = np.linspace(x_sort[0], x_sort[-1], 100000)
data = np.array(df['dmm_burst_volt_timer_mean'] - offset)
s_fit = inter.UnivariateSpline (x_sort, data[x_idx], s=0.001)

PLOT_FIT = True
if PLOT_FIT:
	plt.plot(x_fit, s_fit(x_fit), 'r')

# use fit to find phase of zero-crossing 
#	find sign change and positive going
print('-'*60)
print('ADA2200 phase analysis to compare to datasheet figure 15')
sign_fit = np.sign(s_fit(x_fit))
sign_change = sign_fit[1:]*sign_fit[0:-1]

pos_zerocross = np.intersect1d(np.where(sign_fit < 0), np.where(sign_change == -1))
print('Pos zero cross = {}'.format(x_fit[pos_zerocross[0]]))

# use fit to find max and min voltage values and determine conversion value

# get function generator amplitude from baseline measurements (pk-pk)
fgen_v = header.table('baseline')['fgen_v'].iloc[0] 

maxval = np.max(s_fit(x_fit))
minval = np.min(s_fit(x_fit))
print('Max value = {}'.format(np.max(maxval)))
print('Min value = {}'.format(np.max(minval)))

print('Conversion gain from max = {}'.format(maxval/(2/(fgen_v*np.sqrt(2)))))
print('Conversion gain from min = {}'.format(minval/(2/(fgen_v*np.sqrt(2)))))
print('-'*60)
