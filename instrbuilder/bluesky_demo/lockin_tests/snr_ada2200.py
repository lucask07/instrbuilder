
# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas


"""
Use RCLK as the input signal
need a high-input impedance square-wave to sine wave generator
[or maybe don't bother with conversion]
(but limit phase shift), since the attenuators
load the signal and then the multimeter isn't triggered

Use the same setup for dynamic reserve
    Function generator can inject the signal
"""


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

# use symbolic links
sys.path.append('/Users/koer2434/ophyd/ophyd/')
sys.path.append(
    '/Users/koer2434/instrbuilder/')

# imports that require sys.path.append pointers
from ophyd.device import Kind
from ophyd.ee_instruments import FunctionGen, MultiMeter, Oscilloscope, \
                                 ManualDevice, BasicStatistics, FilterStatistics
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
#           Multimeter
# ------------------------------------------------

dmm = MultiMeter(name='dmm')

# configure for fast burst reads
dmm.volt_autozero_dc.set(0)
dmm.volt_aperture.set(20e-6)

# create an object that returns statistics calculated on the arrays returned by read_buffer
# the name is derived from the parent (e.g. lockin and from the signal that returns an array e.g. read_buffer)
dmm_burst_stats = BasicStatistics(name='', array_source=dmm.burst_volt_timer)
dmm_filter_stats = FilterStatistics(name='', array_source=dmm.burst_volt_timer)


# ------------------------------------------------
#           Attenuator (must be manually changed)
# ------------------------------------------------
att = ManualDevice(name='att')


# ------------------------------------------------
#   Run a measurement (with a custom per step)
# ------------------------------------------------
from bluesky.plan_stubs import checkpoint, abs_set, trigger_and_read, pause


def custom_step(detectors, motor, step):
    """
    Inner loop of a 1D step scan
    Modified the default function for ``per_step`` param in 1D plans.
    Add a pause to adjust the attenuator
    """
    yield from checkpoint()
    print('Set attenuator to {}'.format(step))
    yield from pause()

    yield from abs_set(motor, step, wait=True)
    return (yield from trigger_and_read(list(detectors) + [motor]))


# -----------------------------------------------------
#                   Run a Measurement: sweep FG phase
# ----------------------------------------------------
dmm.burst_volt_timer.stage()

# burst read configuration
#                                                  configs={'reads_per_trigger': 8, 'aperture': 20e-6,
#                                                           'trig_source': 'EXT', 'trig_count': 1024,
#                                                           'sample_timer': 102.4e-6, 'repeats': 1})
# captures 8192 over 0.838 seconds

time.sleep(0.1)

phase = osc.meas_phase.get()
print('Measured phase of {}'.format(phase))
# fg.phase.set(-phase)

print('starting plan!')

uid = RE(
    list_scan([dmm.burst_volt_timer, dmm_burst_stats.mean,
               dmm_filter_stats.filter_6dB_mean, dmm_filter_stats.filter_24dB_mean,
               dmm_filter_stats.filter_6dB_std, dmm_filter_stats.filter_24dB_std],
              att.val, [3, 6, 10, 20, 30, 50, 80], per_step=custom_step),
    LiveTable([att.val, dmm.burst_volt_timer]),
    # the parameters below will be metadata
    attenuator='attenuator sweep',
    purpose='snr_ADA2200',
    operator='Lucas',
    dut='ADA2200',
    preamp='yes_AD8655',
    notes='modified setup and measured amp; switch to 50Ohm output for FGs'
)

# the script does not continue along

print('finished plan!')
# ------------------------------------------------
#   	(briefly) Investigate the captured data
# ------------------------------------------------

# get data into a pandas data-frame
uid = '7bf78db6-4953-4249-8918-614c903fa9c1'
header = db[uid]  # db is a DataBroker instance
print(uid)
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
h = db[-1]
df_meta = h.table('baseline')
