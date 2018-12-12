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

from ophyd.device import Kind
from ophyd.ee_instruments import LockIn, FunctionGen, MultiMeter

RE = RunEngine({})
db = Broker.named('local_file')  # a broker poses queries for saved data sets

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)

# -------------------------------------
#			Function Generator
# -------------------------------------

fg = FunctionGen(name='fg')
if fg.unconnected:
    sys.exit('Function Generator is not connected, exiting blueksy demo')
RE.md['lock_in'] = fg.id.get()

# setup control of the frequency sweep
fg.freq.delay = 0.2
fg.freq.kind = Kind.hinted

dmm = MultiMeter(name = 'name')

# ############# ------------------------------ #############
# #					Setup Supplemental Data				 #
# ############# ------------------------------ #############
from bluesky.preprocessors import SupplementalData
baseline_dets = []
for dev in [dmm, lia]:
    for name in dev.component_names:
        if getattr(dev, name).kind == Kind.config:
            baseline_dets.append(getattr(dev, name))

sd = SupplementalData(baseline=baseline_dets, monitors=[], flyers=[])
RE.preprocessors.append(sd)

############# ------------------------------ #############
#					Run a measurement					 #
############# ------------------------------ #############
dmm.burst_volt.stage()

for i in range(1):
    # scan is a pre-configured Bluesky plan, which returns the experiment uid
    uid = RE(
        #scan([dmm.burst_volt, dmm.isum, dmm.istd], fg.freq, 95, 99, 8),
        scan([dmm.burst_volt], fg.freq, 95, 99, 8),
        LiveTable([fg.freq, dmm.burst_volt, dmm.isum, dmm.istd]),
        # the input parameters below will be metadata
        attenuator='0dB',
        purpose='demo',
        operator='Lucas',
        dut='ADA2200')
