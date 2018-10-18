# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports
import sys
import os
import time
import functools

# imports that may need installation
import numpy as np
from bluesky import RunEngine
from bluesky.callbacks import LiveTable, LivePlot
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import grid_scan, count
import bluesky.preprocessors as bpp
import bluesky.plan_stubs as bps
from bluesky.utils import Msg
from bluesky import utils
from databroker import Broker

from ophyd.device import Kind
from ophyd.ee_instruments import LockIn, FunctionGen, FunctionGen2, ManualDevice, BasicStatistics
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
lia.reset.set(0)
RE.md['lock_in'] = lia.id.get()

# setup lock-in
# similar to a stage, but specific to this experiment
test_frequency = 5e6/512/8
lia.reset.set(None)
lia.fmode.set('Ext')
lia.in_gnd.set('float')
lia.in_config.set('A')
lia.in_couple.set('DC')
lia.freq.set(test_frequency)
lia.sensitivity.set(20e-6)  # 20 uV RMS full-scale
tau = 0.1
lia.tau.set(tau)
# maximum settle to 99% accuracy is 9*tau for a filter-slope of 24-db/oct
# max_settle = 9*tau*4

max_settle = 12*tau
lia.filt_slope.set('24-db/oct')
lia.res_mode.set('normal')

lia.ch1_disp.set('R')  # magnitude, i.e. sqrt(I^2 + Q^2)
lia.disp_val.name = 'lockin_A'  # reading the magnitude from the instrument; change the name for clarity
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
fg.load.set(50)
fg.freq.set(test_frequency)
fg.v.set(20e-3)  # gives 90% of full-scale at a sensitivity of 20uV and 60 dB attenuation
fg.offset.set(0)
fg.output.set('ON')

# ------------------------------------------------
#           Function Generator2
# ------------------------------------------------

fg2 = FunctionGen2(name='fg2')
if fg2.unconnected:
    sys.exit('Function Generator is not connected, exiting blueksy demo')
RE.md['fg2'] = fg2.id.get()

# setup control of the frequency sweep
fg2.freq.delay = max_settle
fg2.v.delay = max_settle
# configure the function generator
fg2.reset.set(None)  # start fresh
fg2.function.set('SIN')
fg2.load.set(50)
fg2.freq.set(test_frequency)
fg2.v.set(0.1)
fg2.offset.set(0)
fg2.output.set('OFF')

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

# --------------------------------------------------------
#                   Get a baseline with averaging
# --------------------------------------------------------
uid_baseline = RE(count([lia.disp_val], num=40, delay=0.2),
                  LiveTable(['lockin_A']),
                  # input parameters below are added to metadata
                  attenuator='60dB',
                  purpose='dynamic_reserve_SR810',
                  operator='Lucas',
                  dut='SR810',
                  preamp='yes_AD8655',
                  notes='baseline-no-interferer')

# baseline measurement
baseline = db[uid_baseline[0]].table()
expected_value = np.mean(baseline['lockin_A'])
# --------------------------------------------------------
#                   Run a 2D sweep of the FG2 frequency and amplitude
# --------------------------------------------------------


def calc_error_deviation(value, baseline):
    return abs((value-baseline)/baseline*100)


calc_per_error = functools.partial(calc_error_deviation, baseline=expected_value)


def target_value(detectors, target_field, motor, start, stop,
                  min_step, target_val,
                  calc_function,
                  accuracy,
                  outer_motor=None, outer_steps=None,
                  *, md=None):
    """
    Vendor and modify adaptive_scan for bluesky.plans
    Scan over one variable with adaptively tuned step size
    find the motor value that gets as close (within accuracy)
    to the target_val without exceeding.
    Targets Dynamic Reserve Testing

    Parameters
    ----------
    detectors : list
        list of 'readable' objects
    target_field : string
        data field whose output is the focus of the adaptive tuning
    motor : object
        any 'setable' object (motor, temp controller, etc.)
    start : float
        starting position of motor
    stop : float
        ending position of motor
    min_step : float
        smallest step
    target_val : float
        desired percent deviation
    accuracy : float
        minimum deviation that the final value can be from the
        smallest amplitude that is found to exceed the target value
    outer_motor : object
        a settable object that is stepped before each target_value scan
    outer_steps : list
        a list of positions for the outer motor ([12, 500, 2000])

    md : dict, optional
        metadata

    See Also
    --------
    :func:`bluesky.plans.rel_adaptive_scan`
    """
    if not 0 < min_step:
        raise ValueError("min_step must meet condition of "
                         "max_step > 0")

    _md = {'detectors': [det.name for det in detectors],
           'motors': [motor.name],
           'plan_args': {'detectors': list(map(repr, detectors)),
                         'motor': repr(motor),
                         'start': start,
                         'stop': stop,
                         'min_step': min_step,
                         'target_val': target_val,
                         'accuracy': accuracy,
                         'outer_motor': repr(outer_motor),
                         'outer_steps': outer_steps},
           'plan_name': 'target_value',
           'hints': {},
           }
    _md.update(md or {})
    try:
        dimensions = [(motor.hints['fields'], 'primary')]
    except (AttributeError, KeyError):
        pass
    else:
        _md['hints'].setdefault('dimensions', dimensions)

    @bpp.stage_decorator(list(detectors) + [motor] + [outer_motor])
    @bpp.run_decorator(md=_md)  # run_decorator(), supplanting open_run() and close_run()
    def adaptive_sweep():

        def adaptive_core():
            next_pos = start
            step = (stop - start) / 2

            past_I = None
            cur_I = target_val + 99  # start the while loop
            repeat = 0
            largest_out_of_bound = stop
            cnt = 0

            if stop >= start:
                direction_sign = 1
            else:
                direction_sign = -1

            while cur_I > target_val or ((largest_out_of_bound - next_pos) > accuracy) or repeat < 3:

                debug = False
                if debug:
                    print('Current value = {}; largest_out_of_bound = {}; repeat = {}'.format(cur_I,
                                                                                              largest_out_of_bound,
                                                                                              repeat))
                yield Msg('checkpoint')
                yield from bps.mv(motor, next_pos)
                yield Msg('create', None, name='primary')
                for det in detectors:
                    yield Msg('trigger', det, group='B')
                yield Msg('wait', None, 'B')
                for det in utils.separate_devices(detectors + [motor] + [outer_motor]):
                    cur_det = yield Msg('read', det)
                    if target_field in cur_det:
                        cur_I = calc_function(value=cur_det[target_field]['value'])
                yield Msg('save')

                # special case first first loop
                if past_I is None:
                    past_I = cur_I
                    next_pos += step * direction_sign
                    continue

                # binary search
                if cur_I > past_I:
                    if cur_I < target_val:
                        direction_sign = 1
                    else:
                        direction_sign = -1
                        largest_out_of_bound = np.min([largest_out_of_bound, next_pos])
                elif cur_I <= past_I:
                    if cur_I < target_val:
                        direction_sign = 1
                    else:
                        direction_sign = -1
                        largest_out_of_bound = np.min([largest_out_of_bound, next_pos])
                else:
                    print('binary search error')

                # the logic here is non-conventional:
                #   once the dynamic reserve is exceeded measurements jump around significantly
                #   so we search for the largest interfering amplitude that does NOT cause a
                #   deviation over 5% (target_val)
                #   and that is a specified voltage maximum voltage away from an interferer amplitude that did cause
                #   a deviation greater than the target value.

                past_I = cur_I
                step = np.max([step/2, min_step])
                if (cur_I < target_val) and (abs(largest_out_of_bound - next_pos) < accuracy):
                    repeat += 1
                    next_pos = next_pos
                else:
                    repeat = 0
                    next_pos += step * direction_sign
                    next_pos = np.clip(next_pos, start, stop)  # by binary search this shouldn't be needed. Just in case

                # handle conditions that might get stuck. Only run 30 loops,
                if ((next_pos == start) or (next_pos == stop) and (repeat == 0) and (cnt > 8)) or (cnt > 50):
                    break
                cnt += 1

        def outer_loop():
            for step in outer_steps:
                yield Msg('checkpoint')
                yield from bps.mv(outer_motor, step)
                yield from adaptive_core()

        return (yield from outer_loop())
    return (yield from adaptive_sweep())


freq_arr = np.logspace(1.8, 4.5, 40)  # 63 - 31622
harmonic_multiplier = np.array([1, 0.998, 1.002, 1.03, 0.97, 1.01, 0.99])
harmonics = [1/3, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9]

harmonics = [0.5, 1, 2]
freq_arr = np.array([])

for hrm in harmonics:
    freq_arr = np.append(freq_arr, test_frequency*hrm*harmonic_multiplier)
freq_arr = np.sort(freq_arr)
print('Total number of points: {}'.format(len(freq_arr)))

fg2.output.set('ON')
fg2.freq.set(freq_arr[0])
time.sleep(tau*12)

uid = RE(target_value([lia.disp_val], 'lockin_A',
         motor=fg2.v, start=0.02, stop=8,
         min_step=0.025, target_val=5,
         calc_function=calc_per_error, accuracy=50e-3,
         outer_motor=fg2.freq, outer_steps=freq_arr),
         LiveTable(['lockin_A', 'fgen2_freq', 'fgen2_v']),
         # input parameters below are added to metadata
         attenuator_fg1='60dB',
         attenuator_fg2='20dB',
         purpose='dynamic_reserve_SR810',
         operator='Lucas',
         dut='SR810',
         preamp='yes_AD8655',
         notes='modified setup and measured amp; switch to 50Ohm output for FGs',
         transfer_function_fg1='0.00193',
         transfer_function_fg2='0.19',
         fg_config=fg.read_configuration(),
         fg2_config=fg2.read_configuration(),
         lia_config=lia.read_configuration())

'''
uid = RE(grid_scan([lia.disp_val],
         fg2.freq, f1, f2, 18,
         fg2.v, 0.02, 0.5, 15, False),
         LiveTable(['lockin_A', 'fgen2_freq', 'fgen2_v']),
         # input parameters below are added to metadata
         attenuator='60dB',
         purpose='dynamic_reserve_SR810',
         operator='Lucas',
         dut='SR810',
         preamp='yes_AD8655',
         fg_config=fg.read_configuration(),
         lia_config=lia.read_configuration())
'''
# ------------------------------------------------
#   	(briefly) Investigate the captured data
# ------------------------------------------------

# baseline measurement
baseline = db[uid_baseline[0]].table()
expected_value = np.mean(baseline['lockin_A'])

# get data into a pandas data-frame
header = db[uid[0]]  # db is a DataBroker instance
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
h = db[-1]
df_meta = h.table('baseline')

# print('These configuration values are saved to baseline data:')
# print(df_meta.columns.values)

import matplotlib.pyplot as plt
'''
for int_v in df['fgen2_v'].unique():
    idx = (df['fgen2_v'] == int_v)
    x = df.loc[idx]['fgen2_freq']
    y = (df.loc[idx]['lockin_A'] - expected_value)/expected_value*100
    plt.semilogx(x, y, marker='*', label='{:0.2f} V'.format(int_v))
plt.legend()
'''

plt.plot(df['fgen2_v'], df['lockin_A'], marker='*')
