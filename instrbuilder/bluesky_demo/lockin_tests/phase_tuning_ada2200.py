# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# TODO: port Aardvark to bluesky


# standard library imports
import sys
import os

# imports that may need installation
import matplotlib.pyplot as plt
import numpy as np
from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import scan, count
from bluesky.utils import Msg
from databroker import Broker

# use symbolic links
sys.path.append('/Users/koer2434/ophyd/ophyd/')
sys.path.append(
    '/Users/koer2434/instrbuilder/')

# imports that require sys.path.append pointers
from ophyd.device import Kind
from ophyd.ee_instruments import MultiMeter, FunctionGen, BasicStatistics, Oscilloscope
import scpi

sys.path.append('/Users/koer2434/Google Drive/UST/research/point_of_care/lock_in/cots_comparisons/ada2200/')
from ada2200 import *

base_dir = os.path.abspath(
    os.path.join(os.path.dirname(scpi.__file__), os.path.pardir))

RE = RunEngine({})
bec = BestEffortCallback()
# Send all metadata/data captured to the BestEffortCallback.
# RE.subscribe(bec) # in this demo we will explicitly define LiveTables and Plots

db = Broker.named('local_file')  # a broker poses queries for saved data sets

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)

# ------------------------------------------------
#           Function Generator
# ------------------------------------------------

fg = FunctionGen(name='fg')
if fg.unconnected:
    sys.exit('Function Generator is not connected, exiting blueksy demo')
RE.md['fg'] = fg.id.get()

# setup control of the frequency sweep
fg.freq.delay = 0.05
fg.phase.delay = 0.05

# configure the function generator
freq_center = 5e6/512/8
fg.reset.set(None)  # start fresh
fg.function.set('SIN')
fg.load.set('INF')
fg.freq.set(freq_center)
fg.v.set(2)  # full-scale range with 1 V RMS sensitivity is 2.8284
fg.offset.set(1.65)
fg.output.set('ON')

dmm = MultiMeter(name='dmm')
osc = Oscilloscope(name='osc')

osc.time_reference.set('CENT')
osc.time_scale.set(200e-6)
osc.acq_type.set('NORM')
osc.trigger_slope.set('POS')
osc.trigger_sweep.set('NORM')
osc.trigger_level_chan2.set(0.7)

# ------------------------------------------------
#           Setup Supplemental Data
# ------------------------------------------------
from bluesky.preprocessors import SupplementalData
baseline_detectors = []
for dev in [fg]:
    for name in dev.component_names:
        if getattr(dev, name).kind == Kind.config:
            baseline_detectors.append(getattr(dev, name))

sd = SupplementalData(baseline=baseline_detectors, monitors=[], flyers=[])
RE.preprocessors.append(sd)

from bluesky.plan_stubs import checkpoint, abs_set, trigger_and_read, sleep

def custom_step(detectors, motor, step):
    """
        Inner loop of a 1D step scan that takes multiple measurements at each step
        with a delay between each measurement
    """
    yield from checkpoint()
    yield from abs_set(motor, step, wait=True)

    num_measurements = 20
    sleep_time = 1

    def finite_loop():
        for _ in range(num_measurements):
            yield Msg('checkpoint')
            yield from trigger_and_read(list(detectors) + [motor])
            # yield Msg('sleep', None, sleep_time)
            yield from sleep(sleep_time)
    return (yield from finite_loop())

# ------------------------------------------------
#                   Run a Measurement
# ------------------------------------------------

for i in range(1):
    # scan is a pre-configured Bluesky plan, which steps one motor
    uid = RE(
        scan([osc.meas_phase], fg.freq,
             freq_center - 0.03, freq_center - 0.005, 20,
             per_step=custom_step),
        LiveTable([fg.freq, osc.meas_phase]),
        # the input parameters below will be metadata
        attenuator='none',
        purpose='phase_tuning',
        operator='Lucas',
        dut='ADA2200')

# ------------------------------------------------
#   	(briefly) Investigate the captured data
# ------------------------------------------------

# get data into a pandas data-frame
header = db[uid[0]]  # db is a DataBroker instance
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
h = db[-1]
df_meta = h.table('baseline')

phase_diff = np.array([])

for f in df['fgen_freq'].unique():
    idx = df.index[df['fgen_freq'] == f].tolist()
    time_diff = (df['time'][idx[0]].to_pydatetime() - df['time'][idx[-1]].to_pydatetime()).total_seconds()
    total_diff = (df['osc_meas_phase'][idx[0]] - df['osc_meas_phase'][idx[-1]])/time_diff
    phase_diff = np.append(phase_diff, total_diff)

plt.plot(df['fgen_freq'].unique(), phase_diff, marker='*')
plt.ylabel('Degree/second')
plt.xlabel('Freq [Hz]')

import scipy.interpolate
y_interp = scipy.interpolate.interp1d(phase_diff, df['fgen_freq'].unique())
optimal_freq = y_interp(0)
print('Frequency of minimum phase drift = {} [Hz]'.format(optimal_freq))

print('Setting Function Generator to lowest phase drift frequency')
fg.freq.set(float(optimal_freq))