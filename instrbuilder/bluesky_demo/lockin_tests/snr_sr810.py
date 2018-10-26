
# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports
import sys
import os
import time

# imports that may need installation
import numpy as np
import matplotlib.pyplot as plt
from bluesky import RunEngine
from bluesky.callbacks import LiveTable, LivePlot
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import list_scan
from databroker import Broker

from ophyd.device import Kind
from ophyd.ee_instruments import LockIn, FunctionGen, MultiMeter, ManualDevice, BasicStatistics
import scpi

RE = RunEngine({})
bec = BestEffortCallback()
# Send all metadata/data captured to the BestEffortCallback.
# RE.subscribe(bec) # in this demo we will explicitly define LiveTables and Plots

db = Broker.named('local_file')  # a broker poses queries for saved data sets

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)

# ------------------------------------------------
#           Lock-In Amplifier
# ------------------------------------------------
lia = LockIn(name='lia')
if lia.unconnected:
    sys.exit('LockIn amplifier is not connected, exiting blueksy demo')

# create an object that returns statistics calculated on the arrays returned by read_buffer
# the name is derived from the parent (e.g. lockin and from the signal that returns an array e.g. read_buffer)
lia_buffer_stats = BasicStatistics(name='', array_source=lia.read_buffer)

lia.reset.set(0)
RE.md['lock_in'] = lia.id.get()

# setup lock-in
# similar to a stage, but specific to this experiment
lia.reset.set(None)
lia.fmode.set('Int')
lia.in_gnd.set('float')
lia.in_config.set('A')
lia.in_couple.set('DC')
lia.freq.set(5000)
lia.sensitivity.set(1.0)  # 1 V RMS full-scale
tau = 0.01
lia.tau.set(tau)
lia.sample_rate.set(32)  # 32 Hz
# maximum settle is 9*tau (filter-slope of 24-db/oct
max_settle = 9*tau
lia.filt_slope.set('6-db/oct')
lia.res_mode.set('normal')

# setup control of the lock-in filter-slope sweep (for LiveTable)
lia.filt_slope.delay = max_settle
lia.filt_slope.kind = Kind.hinted
lia.filt_slope.dtype = 'string'
lia.filt_slope.precision = 9  # so the string is not cutoff in the LiveTable
lia.ch1_disp.set('R')  # magnitude, i.e. sqrt(I^2 + Q^2)
# ------------------------------------------------
#           Function Generator
# ------------------------------------------------

fg = FunctionGen(name='fg')
if fg.unconnected:
    sys.exit('Function Generator is not connected, exiting blueksy demo')
RE.md['lock_in'] = fg.id.get()

# setup control of the frequency sweep
fg.freq.delay = max_settle

# configure the function generator
fg.reset.set(None)  # start fresh
fg.function.set('SIN')
fg.load.set('INF')
fg.freq.set(5000)
fg.v.set(2)
fg.offset.set(0)
fg.output.set('ON')

# ------------------------------------------------
#           Attenuator (must be manually changed)
# ------------------------------------------------
att = ManualDevice(name='att')

# ------------------------------------------------
#           Setup Supplemental Data
# ------------------------------------------------
from bluesky.preprocessors import SupplementalData
baseline_detectors = []
for dev in [fg, lia]:
    for name in dev.component_names:
        if getattr(dev, name).kind == Kind.config:
            baseline_detectors.append(getattr(dev, name))

sd = SupplementalData(baseline=baseline_detectors, monitors=[], flyers=[])
RE.preprocessors.append(sd)

# ------------------------------------------------
#   Run a measurement (with a custom per step)
# ------------------------------------------------
from bluesky.plan_stubs import checkpoint, abs_set, trigger_and_read, pause


def custom_step(detectors, motor, step):
    """
    Inner loop of a 1D step scan

    This is the default function for ``per_step`` param in 1D plans.
    """
    yield from checkpoint()
    print('Set attenuator to {}'.format(step))
    yield from pause()
    yield from abs_set(motor, step, wait=True)
    return (yield from trigger_and_read(list(detectors) + [motor]))


lia.read_buffer.unstage()
lia.read_buffer.stage()
print('Starting scan')
lia.read_buffer.trigger()
time.sleep(0.2)


uid = RE(list_scan([lia.read_buffer, lia_buffer_stats.std, lia_buffer_stats.mean],
         att.val, [0, 6, 10, 20, 30, 50, 60, 70, 80, 90, 100, 110], per_step=custom_step),
         LiveTable([att.val, lia.read_buffer, lia_buffer_stats.mean, lia_buffer_stats.std]),
         attenuator='attenuator sweep',
         purpose='snr_SR810',
         operator='Lucas',
         dut='SR810',
         fg_config=fg.read_configuration(),
         lia_config=lia.read_configuration()
         )

# ------------------------------------------------
#   	(briefly) Investigate the captured data
# ------------------------------------------------

# get data into a pandas data-frame
header = db[uid[0]]  # db is a DataBroker instance
print(uid)
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
h = db[-1]
df_meta = h.table('baseline')

print('Check values saved to baseline data:')
print(df_meta.columns.values)

array_filename = df['lockin_read_buffer'][5]
arr = np.load(os.path.join(lia.read_buffer.save_path, array_filename))
plt.plot(arr)