
# standard library imports
import os

# imports that may need installation
import matplotlib.pyplot as plt
from matplotlib import rcParams
from databroker import Broker

from plot_configs import params, dpi, figure_dir

rcParams.update(params)
rcParams.update(params)


db = Broker.named('local_file')  # a broker poses queries for saved data sets)

# get data into a pandas data-frame
uid = '6c22a3cf-5851-49c8-9086-77f759701284'
header = db[uid]
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
df_meta = header.table('baseline')

fig = plt.figure(dpi=dpi)
ax = fig.add_subplot(2, 1, 1)
ax.plot(df['att_val'], df['lockin_read_buffer_mean'], marker='x')
plt.grid(True)
ax.set(xlabel='Attenuation [dB]', ylabel='R [V RMS]')
ax.set_yscale('log')

ax2 = fig.add_subplot(2, 1, 2)
ax2.plot(df['att_val'], df['lockin_read_buffer_std'], marker='x')
ax2.set(xlabel='Attenuation. [dB]', ylabel='Noise R [V RMS]')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(figure_dir, 'snr_sr810.eps'))