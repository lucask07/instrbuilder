# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# TODO: port Aardvark to bluesky


# standard library imports
import sys
import os

sys.path.append(
    '/Users/koer2434/Google Drive/UST/research/bluesky/my_bluesky/')

# imports that may need installation
from my_bluesky import RunEngine
from my_bluesky.callbacks import LiveTable
from my_bluesky.callbacks.best_effort import BestEffortCallback
from my_bluesky.plans import count
from my_bluesky.plan_stubs import trigger_and_read, trigger
from databroker import Broker

from ophyd.ee_instruments import MultiMeter, FunctionGen, BasicStatistics, Oscilloscope
import scpi

RE = RunEngine({})
bec = BestEffortCallback()
# Send all metadata/data captured to the BestEffortCallback.
# RE.subscribe(bec) # in this demo we will explicitly define LiveTables and Plots

db = Broker.named('local_file')  # a broker poses queries for saved data sets

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)


# Oscilloscope Channel 1 is RCLK from ADA2200
# Oscilloscope Channel 2 is Input Sinusoid from function generator
osc = Oscilloscope(name='osc')
# osc.time_reference.set('CENT')
osc.time_scale.set(200e-6)
osc.acq_type.set('NORM')
osc.trigger_slope.set('POS')
osc.trigger_sweep.set('NORM')
osc.trigger_level_chan2.set(3.3/2)
osc.trigger_source.set(1)


# ------------------------------------------------
#                   Run a Measurement
# ------------------------------------------------


# scan is a pre-configured Bluesky plan, which steps one motor
uid = RE(
    count([osc.meas_phase], 1),
    LiveTable([osc.meas_phase]),
    # the input parameters below will be metadata
    attenuator='none',
    purpose='fix_trigger_and_read',
    operator='Lucas',
    dut='oscilloscope')
