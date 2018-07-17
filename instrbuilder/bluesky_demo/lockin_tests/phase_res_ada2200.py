# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# TODO:
#  port Aardvark to bluesky
#  add dmm and fg config to metadata (was this causing an error)


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
from databroker import Broker

# symbolic links to local ophyd and instrbuilder
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
fg.reset.set(None)  # start fresh
fg.function.set('SIN')
fg.load.set('INF')
fg.freq.set(1220.680518480077)  # was 5e6/512/8
fg.v.set(2)  # full-scale range with 1 V RMS sensitivity is 2.8284
fg.offset.set(1.65)
fg.output.set('ON')

dmm = MultiMeter(name='dmm')

# configure for fast burst reads
dmm.volt_autozero_dc.set(0)
dmm.volt_aperture.set(20e-6)

# create an object that returns statistics calculated on the arrays returned by read_buffer
# the name is derived from the parent (e.g. lockin and from the signal that returns an array e.g. read_buffer)
dmm_burst_stats = BasicStatistics(name='', array_source=dmm.burst_volt_timer)

# ------------------------------------------------
#           Oscilloscope
# ------------------------------------------------

# Oscilloscope Channel 1 is RCLK from ADA2200
# Oscilloscope Channel 2 is Input Sinusoid from function generator
osc = Oscilloscope(name='osc')
osc.time_reference.set('CENT')
osc.time_scale.set(200e-6)
osc.acq_type.set('NORM')
osc.trigger_slope.set('POS')
osc.trigger_sweep.set('NORM')
osc.trigger_level_chan2.set(3.3/2)
osc.trigger_source.set(1)

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


# -----------------------------------------------------
#                   Run a Measurement: sweep FG phase
# ----------------------------------------------------
dmm.burst_volt_timer.stage()

for i in range(1):
    # scan is a pre-configured Bluesky plan, which steps one motor
    uid = RE(
        scan([dmm.burst_volt_timer, dmm_burst_stats.mean, osc.meas_phase], fg.phase,
             0, 360, 60),
        LiveTable([fg.phase, osc.meas_phase, dmm.burst_volt_timer, dmm_burst_stats.mean]),
        # the parameters below will be metadata
        attenuator='0dB',
        purpose='phase_dependence',
        operator='Lucas',
        dut='ADA2200')


# -----------------------------------------------------
#                 Find offset voltage
# ----------------------------------------------------

fg.freq.set(20000)  # detune frequency
fg.v.set(2e-3)  # Minimum amplitude

# slow DMM setting
dmm.volt_autozero_dc.set(1)
dmm.volt_aperture.set(100e-3)

for i in range(1):
    # scan is a pre-configured Bluesky plan, which steps one motor
    uid_offset = RE(
        count([dmm.meas_volt_dc], num=10),
        LiveTable([dmm.meas_volt_dc]),
        # the parameters below will be metadata
        attenuator='0dB',
        purpose='phase_dependence_offset',
        operator='Lucas',
        dut='ADA2200')

# ------------------------------------------------
#   	(briefly) Investigate the captured data
# ------------------------------------------------

# get offset voltage
header = db[uid_offset[0]]  # db is a DataBroker instance
df = header.table()
offset = np.mean(df['dmm_meas_volt'])
print('Offset measured as: {} [V]'.format(offset))

# get data into a pandas data-frame
header = db[uid[0]]  # db is a DataBroker instance
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
h = db[-1]
df_meta = h.table('baseline')

print('These configuration values are saved to baseline data:')
print(df_meta.columns.values)

array_filename = df['dmm_burst_volt_timer'][1]
arr = np.load(os.path.join(dmm.burst_volt_timer.save_path, array_filename))
plt.plot(arr, marker='*', LineStyle='None')

plt.figure()
plt.plot(df['osc_meas_phase'], df['dmm_burst_volt_timer_mean'] - offset,
         marker='*', LineStyle='None')
plt.xlabel('Phase [deg]')
plt.ylabel('Magnitude [V]')
plt.grid(True)
