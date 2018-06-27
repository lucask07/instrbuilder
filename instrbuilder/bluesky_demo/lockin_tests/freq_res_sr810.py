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

# -------------------------------------
#           Lock-In Amplifier
# -------------------------------------
lia = LockInAuto(name='lia')
if lia.unconnected:
    sys.exit('LockIn amplifier is not connected, exiting blueksy demo')
lia.reset.set(0)
RE.md['lock_in'] = lia.id.get()

# setup lock-in
# similar to a stage, but specific to this experiment
lia.freq.set(5000)
lia.sensitivity.set(26)
lia.tau.set(8)
lia.filt_slope.set('6-db/oct')

# -------------------------------------
#           Function Generator
# -------------------------------------

fg = FunctionGenAuto(name='fg')
if fg.unconnected:
    sys.exit('Function Generator is not connected, exiting blueksy demo')
RE.md['lock_in'] = fg.id.get()

# setup control of the frequency sweep
fg.freq.delay = 0.2
fg.freq.kind = Kind.hinted

# -------------------------------------
#           Setup Supplemental Data
# -------------------------------------
from bluesky.preprocessors import SupplementalData
baseline_dets = []
for dev in [fg, lia]:
    for name in dev.component_names:
        if getattr(dev, name).kind == Kind.config:
            baseline_dets.append(getattr(dev, name))

sd = SupplementalData(baseline=baseline_dets, monitors=[], flyers=[])
RE.preprocessors.append(sd)

# ------------------------------------------------
#                   Run a 2D sweep
# ------------------------------------------------
# setup control of the lock-in filter-slope sweep
lia.filt_slope.delay = 2
lia.filt_slope.kind = Kind.hinted
# ToDo: pass datatypes to bluesky automatically
lia.filt_slope.dtype = 'string'

if len(addr) != 0:
    for i in range(1):
        # grid_scan is a pre-configured Bluesky plan; returns the experiment uid
        uid = RE(
            grid_scan([lia.disp_val],
                lia.filt_slope, 0, 3, 4,
                fg.freq, 4997, 5005, 30, False),
            LivePlot('disp_val', 'freq'),
            # the input parameters below are metadata
            attenuator='0dB',
            purpose='freq_resolution_SR810',
            operator='Lucas',
            fg_config=fg.read_configuration(),
            lia_config=lia.read_configuration())

# ------------------------------
#   	Example Data Processing
# ------------------------------

# get data into a pandas data-frame
header = db[uid[0]]  # db is a DataBroker instance
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
h = db[-1]
h.table('baseline')