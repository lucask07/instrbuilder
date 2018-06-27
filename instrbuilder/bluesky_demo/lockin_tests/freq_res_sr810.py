# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports
import sys
import os
import time

# imports that may need installation
import matplotlib.pyplot as plt
from bluesky import RunEngine
from bluesky.callbacks import LiveTable, LivePlot
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import scan, grid_scan
from databroker import Broker

# use symbolic links
sys.path.append('/Users/koer2434/ophyd/ophyd/')
sys.path.append(
    '/Users/koer2434/instrbuilder/')

# imports that require sys.path.append pointers
from ophyd.device import Kind
from ophyd.ee_instruments import LockInAuto, FunctionGenAuto, MultiMeterAuto
import scpi

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
#           Lock-In Amplifier
# ------------------------------------------------
lia = LockInAuto(name='lia')
if lia.unconnected:
    sys.exit('LockIn amplifier is not connected, exiting blueksy demo')
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
lia.sensitivity.set(1.0) # 1 V RMS full-scale
tau = 0.1
lia.tau.set(tau)
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

fg = FunctionGenAuto(name='fg')
if fg.unconnected:
    sys.exit('Function Generator is not connected, exiting blueksy demo')
RE.md['lock_in'] = fg.id.get()

# setup control of the frequency sweep
fg.freq.delay = max_settle

# configure the function generator
fg.reset.set(None) # start fresh
fg.function.set('SIN')
fg.load.set('INF')
fg.freq.set(5000)
fg.v.set(2) #full-scale range with 1 V RMS sensitivity is 2.8284
fg.offset.set(0)
fg.output.set('ON')

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
#                   Run a 2D sweep
# ------------------------------------------------

# grid_scan is a pre-configured Bluesky plan
uid = RE(
    grid_scan([lia.disp_val],
        lia.filt_slope, 0, 1, 1,
        fg.freq, 4997, 5005, 10, False),
    LiveTable(['lockin_disp_val', 'fgen_freq', 'lockin_filt_slope']),
    # input parameters below are added to metadata
    attenuator='0dB',
    purpose='freq_resolution_SR810',
    operator='Lucas',
    fg_config=fg.read_configuration(),
    lia_config=lia.read_configuration())

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

print('Check values saved to baseline data:')
print(df_meta.columns.values)