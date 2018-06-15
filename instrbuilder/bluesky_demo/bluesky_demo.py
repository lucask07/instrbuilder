# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports
import sys
import os
import time
import functools
import itertools
from itertools import chain
from collections import (Iterable, defaultdict)

# imports that may need installation
import numpy as np
import matplotlib.pyplot as plt
from bluesky import RunEngine
from bluesky.callbacks import LiveTable, LivePlot
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import scan, count, grid_scan
from bluesky import plan_stubs as bps
from bluesky.utils import (separate_devices, all_safe_rewind, Msg,
                    short_uid as _short_uid)

import itertools
import uuid
from cycler import cycler
from bluesky import utils
import operator
from functools import reduce

try:
    # cytools is a drop-in replacement for toolz, implemented in Cython
    from cytools import partition
except ImportError:
    from toolz import partition


from bluesky.utils import (separate_devices, all_safe_rewind, Msg,
                    short_uid as _short_uid)

from databroker import Broker

# use symbolic links
sys.path.append(
    '/Users/koer2434/ophyd/')  # these 2 will become an import of ophyd
sys.path.append('/Users/koer2434/ophyd/ophyd/')  #
sys.path.append(
    '/Users/koer2434/instrbuilder/')  # this instrbuilder: the SCPI library

# imports that require sys.path.append pointers
from ophyd.scpi import ScpiSignal, ScpiSignalBase, ScpiSignalFileSave, StatCalculator
from ophyd import Device, Component
from ophyd.device import Kind
from scpi import init_instrument, SCPI
from instruments import SRSLockIn, AgilentFunctionGen
import scpi

base_dir = os.path.abspath(
    os.path.join(os.path.dirname(scpi.__file__), os.path.pardir))

plt.close('all')

RE = RunEngine({})
bec = BestEffortCallback()
# Send all metadata/data captured to the BestEffortCallback.
# RE.subscribe(bec) # the BestEffortCallback seems to fail too often for my scenarios
                    #       will explicitly define LiveTables and Plots

db = Broker.named('local_file')  # a broker poses queries for saved data sets

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)

def my_trigger_and_read(devices, name='primary'):
    """
    Trigger and read a list of detectors and bundle readings into one Event.

    Parameters
    ----------
    devices : iterable
        devices to trigger (if they have a trigger method) and then read
    name : string, optional
        event stream name, a convenient human-friendly identifier; default
        name is 'primary'

    Yields
    ------
    msg : Msg
        messages to 'trigger', 'wait' and 'read'
    """
    # If devices is empty, don't emit 'create'/'save' messages.
    if not devices:
        yield from null()
    devices = separate_devices(devices)  # remove redundant entries
    rewindable = all_safe_rewind(devices)  # if devices can be re-triggered

    def inner_trigger_and_read():
        grp = _short_uid('trigger')
        no_wait = True
        for obj in devices:
            print('inner trigger and read')
            if hasattr(obj, 'trigger'):
                no_wait = False
                yield from trigger(obj, group=grp)
        # Skip 'wait' if none of the devices implemented a trigger method.
        if not no_wait:
            yield from wait(group=grp)
        yield from create(name)
        ret = {}  # collect and return readings to give plan access to them
        for obj in devices:
            reading = (yield from read(obj))
            if reading is not None:
                ret.update(reading)
        yield from save()
        return ret
    from bluesky.preprocessors import rewindable_wrapper
    return (yield from rewindable_wrapper(inner_trigger_and_read(),
                                          rewindable))

def my_one_1d_step(detectors, motor, step):
    """
    Inner loop of a 1D step scan

    This is the default function for ``per_step`` param in 1D plans.
    """
    def move():
        grp = _short_uid('set')
        yield Msg('checkpoint')
        yield Msg('set', motor, step, group=grp)
        yield Msg('wait', None, group=grp)

    print('My per step')
    yield from move()
    return (yield from my_trigger_and_read(list(detectors) + [motor]))

############# ------------------------------ #############
#					Lock-in Amplifier 					 #
############# ------------------------------ #############
# get lockin amplifier SCPI object
instrument_path = 'instruments/srs/lock_in/sr810/'
cmd_name = 'commands.csv'
lookup_name = 'lookup.csv'
cmd_map = os.path.join(base_dir, instrument_path, cmd_name)
lookup_file = os.path.join(base_dir, instrument_path, lookup_name)
addr = {'pyserial': '/dev/tty.USA19H14112434P1.1'}

# addr = {} # an empty address dictionary will return an unconnected instrument
#   that can be used for simulations
cmd_list, inst_comm, unconnected = init_instrument(
    cmd_map, addr=addr, lookup=lookup_file, init_write='OUTX 0')
scpi_lia = SRSLockIn(cmd_list, inst_comm, name='lock-in', unconnected=unconnected)
# reset the lockin amplifier
scpi_lia.set(0, 'reset')

# Immediately add the lock-in instrument id to the run-engine metadata
RE.md['lock_in'] = scpi_lia.vendor_id


# create a Bluesky Lock-in device
class LockIn(Device):
    fmode = Component(ScpiSignal, scpi_cl=scpi_lia, cmd_name='fmode', configs={})
    tau = Component(ScpiSignal, scpi_cl=scpi_lia, cmd_name='tau', configs={})
    ch1_disp = Component(
        ScpiSignal, scpi_cl=scpi_lia, cmd_name='ch1_disp', configs={'ratio': 0})
    freq = Component(ScpiSignal, scpi_cl=scpi_lia, cmd_name='freq', configs={})
    disp_val = Component(
        ScpiSignal, scpi_cl=scpi_lia, cmd_name='disp_val', configs={})
    filt_slope = Component(
        ScpiSignal, scpi_cl=scpi_lia, cmd_name='filt_slope', configs={})
    read_buffer = Component(ScpiSignalFileSave, name='img', 
                            scpi_cl=scpi_lia, cmd_name='read_buffer', 
                            save_path = '/Users/koer2434/Google Drive/UST/research/bluesky/data',
                            kind = Kind.normal,
                            precision = 10,
                            configs = {'start_pt': 0, 'num_pts' : 20}) # this won't print the full file name, but enough to be unique
    # Stats on the array 
    isum = Component(StatCalculator, name = 'sum', img = None, 
        stat_func = np.sum, kind=Kind.hinted)
    istd = Component(StatCalculator, name = 'std', img = None, 
        stat_func = np.std, kind=Kind.hinted)
    # Example of an Instrbuilder long setter, i.e. the SCPI command takes more than a single value
    off_exp = ScpiSignal(
        scpi_cl=scpi_lia, cmd_name='off_exp', configs={'chan':
                                                  2})  # offset and expand

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.isum._img = self.read_buffer


    def stage(self):
        self.tau.set(8)
        self.fmode.set('Int')
        self.ch1_disp.set('X')  # magnitude
        self.freq.set(5e3)

    def unstage(self):
        pass

# create a Bluesky Lock-in device
class LockInBuffer(Device):

    reset_scan = Component(ScpiSignal, scpi_cl=scpi_lia, cmd_name='reset_scan', configs={})
    scan_mode = Component(ScpiSignal, scpi_cl=scpi_lia, cmd_name='scan_mode', configs={})
    sample_rate = Component(ScpiSignal, scpi_cl=scpi_lia, cmd_name='sample_rate', configs={})
    trigger_start = Component(ScpiSignal, scpi_cl=scpi_lia, cmd_name='trigger_start', configs={})
    trigger_lockin = Component(ScpiSignal, scpi_cl=scpi_lia, cmd_name='trigger', configs={})

    status_monitor = {'name': 'data_pts_ready', 'configs':{}, 
                        'threshold_function': lambda read_val,thresh:  read_val > thresh, 
                        'threshold_level': 40,
                        'poll_time': 0.05, 
                        'trig_name': ['reset_scan', 'start_scan', 'trigger'], 
                        'trig_configs': {},
                        'post_name': 'pause_scan',
                        'post_configs': {}}

    read_buffer = Component(ScpiSignalFileSave, name='img', 
                            scpi_cl=scpi_lia, cmd_name='read_buffer', 
                            save_path = '/Users/koer2434/Google Drive/UST/research/bluesky/data',
                            kind = Kind.normal,
                            precision = 10,  # this won't print the full file name, but enough to be unique
                            configs = {'start_pt': 0, 'num_pts' : 10},
                            status_monitor = status_monitor)
    # Stats on the array 
    isum = Component(StatCalculator, name = 'sum', img = None, 
        stat_func = np.sum, kind=Kind.hinted)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.isum._img = self.read_buffer


    def stage(self):
        self.reset_scan.set(None)
        self.scan_mode.set(0)
        self.sample_rate.set(10)
        self.trigger_start.set(1) # trigger starts scan mode
        print('Staging buffered lia')

    def unstage(self):
        self.reset_scan.set(None)
        print('Unstaging buffered lia')


    def trigger(self):
        print('Triggering buffered lia')
        self.read_buffer.trigger() 
        return (self.isum.trigger())


lia = LockIn(name='lia')
lia_buffer = LockInBuffer(name='lia_buff')

for cmpt in ['tau', 'fmode', 'freq']:
    setattr(getattr(lia, cmpt), 'kind', Kind.config)

############# ------------------------------ #############
#					Function Generator 					 #
############# ------------------------------ #############
instrument_path = 'instruments/agilent/function_gen/3320A/'
cmd_name = 'commands.csv'
lookup_name = 'lookup.csv'
cmd_map = os.path.join(base_dir, instrument_path, cmd_name)
lookup_file = os.path.join(base_dir, instrument_path, lookup_name)
addr = {'pyvisa': 'USB0::0x0957::0x0407::MY44060286::INSTR'}
# addr = {}
cmd_list, inst_comm, unconnected = init_instrument(
    cmd_map, addr=addr, lookup=lookup_file)
scpi_fg = AgilentFunctionGen(
    cmd_list, inst_comm, name='function-generator', unconnected=unconnected)

# Immediately add the function generator vendor/instrument_id to the run-engine metadata
RE.md['function_generator'] = scpi_fg.vendor_id


### -------- Example of a device: function generator ---------------
class FuncGen(Device):
    freq = Component(ScpiSignal, scpi_cl=scpi_fg, cmd_name='freq', configs={})
    v = Component(ScpiSignal, scpi_cl=scpi_fg, cmd_name='v', configs={})
    output = Component(ScpiSignal, scpi_cl=scpi_fg, cmd_name='output', configs={})
    offset = Component(ScpiSignal, scpi_cl=scpi_fg, cmd_name='offset', configs={})

    def stage(self):
        self.freq.set(4997)
        self.v.set(0.01)
        self.offset.set(0)
        if self.output.get() == 'OFF':
            self.output.set('ON')

    def unstage(self):
        # could/should turn the output off, but would rather not cycle the relay every time
        self.freq.set(4997)


fg = FuncGen(name='fg')

# setup control of the frequency sweep
fg.freq.delay = 0.2
fg.freq.kind = Kind.hinted

# TODO: bsky_rg.read_configuration() returns an empty OrderedDict if the configuration_attrs is simply populated
#		read_configuration() depends upon the setting of offset.kind for each component
#		should be = Kind.config
#		Am I doing something wrong or is the documentation stale?
for cmpt in ['output', 'v', 'offset']:
    setattr(getattr(fg, cmpt), 'kind', Kind.config)

############# ------------------------------ #############
#					Setup Supplemental Data				 #
############# ------------------------------ #############
from bluesky.preprocessors import SupplementalData
baseline_dets = []
for dev in [fg, lia]:
    for name in dev.component_names:
        if getattr(dev, name).kind == Kind.config:
            baseline_dets.append(getattr(dev, name))

sd = SupplementalData(baseline=baseline_dets, monitors=[], flyers=[])
RE.preprocessors.append(sd)

############# ------------------------------ #############
#					Run a measurement					 #
############# ------------------------------ #############

# stage the instrumetns
lia.stage()
fg.stage()

if len(addr) != 0:
    for i in range(1):
        # scan is a pre-configured Bluesky plan; returns the experiment uid
        uid = RE(
            scan([lia.disp_val], fg.freq, 4997, 5005, 8),
            LiveTable([fg.freq, lia.disp_val]),
            # the input parameters below will be metadata
            attenuator='60dB',
            purpose='demo',
            operator='Lucas',
            fg_config=fg.read_configuration(),
            lia_config=lia.read_configuration())
if 0:
    ############# ------------------------------ #############
    #                   Run a 2D sweep                       #
    ############# ------------------------------ #############
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
                # LiveTable([lia.disp_val]),
                LivePlot('disp_val', 'freq'),
                # the input parameters below will be metadata
                attenuator='60dB',
                purpose='demo',
                operator='Lucas',
                fg_config=fg.read_configuration(),
                lia_config=lia.read_configuration())
            # TODO: the name of the SCPI command becomes the display name used by bluesky,
            #        would like to be able to rename the plot axis

    ############# ------------------------------ #############
    #				Example Data Processing					 #
    ############# ------------------------------ #############

    if len(addr) != 0:
        # get data into a pandas dataframe
        header = db[uid[0]] # db is a DataBroker instance
        print(header.table())
        df = header.table()

        plt.figure()
        for fs in df['filt_slope'].unique():
            idx = (df['filt_slope'] == fs)
            plt.plot(df.loc[idx]['freq'], df.loc[idx]['disp_val'], 
                marker = '*', 
                label = 'Filt. slope = {}'.format(fs))
        plt.legend()
        # metadata
        header['start']
        header['stop']

        # view the baseline data (i.e. configuration values)
        h = db[-1]
        h.table('baseline')

lia_buffer.stage()
lia_buffer.read_buffer.stage()
print('Starting scan')
lia_buffer.read_buffer.trigger()
time.sleep(0.2)
uid = RE(scan([lia_buffer.read_buffer, lia_buffer.isum], 
                    fg.freq, 4997, 5005, 30),
                    #, per_step = my_one_1d_step),
                LiveTable([lia_buffer.read_buffer, lia_buffer.isum]),
                # LivePlot('disp_val', 'freq'),
                # the input parameters below will be metadata
                attenuator='60dB',
                purpose='demo',
                operator='Lucas')

'''
def one_1d_step_multiples(detectors, motor, step, num = 10, delay = 0.1):
    """
    Inner loop of a 1D step scan, with mutliple samples at each point

    Adapted from one_1d_step.
    """
    def move():
        grp = _short_uid('set')
        yield Msg('checkpoint')
        yield Msg('set', motor, step, group=grp)
        yield Msg('wait', None, group=grp)

    yield from move()

    # If delay is a scalar, repeat it forever. If it is an iterable, leave it.
    if not isinstance(delay, Iterable):
        delay = itertools.repeat(delay)
    else:
        try:
            num_delays = len(delay)
        except TypeError:
            # No way to tell in advance if we have enough delays.
            pass
        else:
            if num - 1 > num_delays:
                raise ValueError("num=%r but delays only provides %r "
                                 "entries" % (num, num_delays))
        delay = iter(delay)


    def finite_plan():
        for i in range(num):
            now = time.time()  # Intercept the flow in its earliest moment.
            yield Msg('checkpoint')
            yield from bps.trigger_and_read(detectors)
            try:
                d = next(delay)
            except StopIteration:
                if i + 1 == num:
                    break
                else:
                    # num specifies a number of iterations less than delay
                    raise ValueError("num=%r but delays only provides %r "
                                     "entries" % (num, i))
            if d is not None:
                d = d - (time.time() - now)
                if d > 0:  # Sleep if and only if time is left to do it.
                    yield Msg('sleep', None, d)

    return (yield from finite_plan())
'''