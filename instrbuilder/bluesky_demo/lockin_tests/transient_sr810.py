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
from bluesky.callbacks import LiveTable
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import list_scan
from databroker import Broker

# use symbolic links
sys.path.append('/Users/koer2434/ophyd/ophyd/')
sys.path.append(
    '/Users/koer2434/instrbuilder/')

# imports that require sys.path.append pointers
from ophyd.device import Kind
from ophyd.ee_instruments import LockIn, FunctionGen, Oscilloscope
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
lia = LockIn(name='lia')
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
lia.sensitivity.set(1.0)  # 1 V RMS full-scale
tau = 0.03
lia.tau.set(tau)
# maximum settle to 99% accuracy is 9*tau (filter-slope of 24-db/oct
max_settle = 9*tau*4
lia.filt_slope.set('6-db/oct')
lia.res_mode.set('normal')

# setup control of the lock-in filter-slope sweep (for LiveTable)
lia.filt_slope.delay = max_settle*2
lia.filt_slope.kind = Kind.hinted
lia.filt_slope.dtype = 'string'
lia.filt_slope.precision = 9  # so the string is not cutoff in the LiveTable
lia.ch1_disp.set('R')  # magnitude, i.e. sqrt(I^2 + Q^2)

lia.ch1_out_select.set(0)
# ------------------------------------------------
#           Function Generator
# ------------------------------------------------

fg = FunctionGen(name='fg')
if fg.unconnected:
    sys.exit('Function Generator is not connected, exiting blueksy demo')
RE.md['fg'] = fg.id.get()

# setup control of the frequency sweep
fg.freq.delay = max_settle

# configure the function generator
fg.reset.set(None)  # start fresh
fg.function.set('SIN')
fg.load.set('INF')
fg.freq.set(5000)
fg.v.set(2)  # full-scale range with 1 V RMS sensitivity is 2.8284
fg.offset.set(0)
fg.output.set('ON')

osc = Oscilloscope(name='osc')


osc.time_reference.set('LEFT')
osc.time_scale.set(20e-3)
osc.acq_type.set('NORM')
osc.trigger_slope.set('POS')
osc.trigger_sweep.set('NORM')
osc.trigger_level_chan2.set(0.7)


from bluesky.plan_stubs import checkpoint, abs_set, trigger_and_read


def custom_step(detectors, motor, step):
    """
    Inner loop of a 1D step scan

    This is the default function for ``per_step`` param in 1D plans.
    """
    yield from checkpoint()
    fg.output.set(0)
    print('Output off')
    yield from abs_set(motor, step, wait=True)
    osc.single_acq.set(None)
    time.sleep(0.1)
    fg.output.set(1)
    print('Output on')
    time.sleep(1)
    return (yield from trigger_and_read(list(detectors) + [motor]))


osc.display_data.stage()
time.sleep(0.2)
lia.tau.delay = 0.5

uid = RE(list_scan([osc.display_data],
         lia.tau, [100e-6, 10e-3], per_step=custom_step),
         LiveTable([lia.tau, osc.display_data]),
         attenuator='attenuator sweep',
         purpose='snr_SR810',
         operator='Lucas',
         dut='SR810',
         fg_config=fg.read_configuration(),
         lia_config=lia.read_configuration()
         )

fg.output.set('OFF')

# ------------------------------------------------
#   	(briefly) Investigate the captured data
# ------------------------------------------------

# get data into a pandas data-frame
# header = db[uid[0]]  # db is a DataBroker instance
# print(header.table())
# df = header.table()
# # view the baseline data (i.e. configuration values)
# h = db[-1]
# df_meta = h.table('baseline')
#
# print('These configuration values are saved to baseline data:')
# print(df_meta.columns.values)
