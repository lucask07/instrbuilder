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
#			Function Generator
# -------------------------------------

fg = FunctionGenAuto(name='fg')
if fg.unconnected:
    sys.exit('Function Generator is not connected, exiting blueksy demo')
RE.md['lock_in'] = fg.id.get()

# setup control of the frequency sweep
fg.freq.delay = 0.2
fg.freq.kind = Kind.hinted

dmm = MultiMeterAuto(name = 'name')

# # TODO: Best methods to read configurations?
# #       1) as below, append to supplemental data: to SQL
# #       2) assign a metadata parameter to instrument.read_configuration(): to JSON
# #       3) both?: means read twice
# #       4) the answer might be the following: if the information is used in data analysis put in the SQL
# #                                             if the information is used to sort files, etc. put into JSON

# ############# ------------------------------ #############
# #					Setup Supplemental Data				 #
# ############# ------------------------------ #############
# from bluesky.preprocessors import SupplementalData
# baseline_dets = []
# for dev in [fg, lia]:
#     for name in dev.component_names:
#         if getattr(dev, name).kind == Kind.config:
#             baseline_dets.append(getattr(dev, name))

# sd = SupplementalData(baseline=baseline_dets, monitors=[], flyers=[])
# RE.preprocessors.append(sd)

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
        operator='Lucas')