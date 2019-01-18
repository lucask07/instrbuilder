# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

"""
Evaluate the dynamic reserve of the ADA2200;

Instruments Used: power supply, multimeter, Aardvark i2c for ADA2200 control

Corresponds to manuscript Figure 9

"""

# standard library imports
import sys
import os
import time
import functools

# imports that may need installation
import numpy as np
import matplotlib.pyplot as plt
from bluesky import RunEngine
from bluesky.callbacks import LiveTable, LivePlot
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import grid_scan, count
import bluesky.preprocessors as bpp
import bluesky.plan_stubs as bps
from bluesky.utils import Msg
from bluesky import utils
from bluesky.plan_stubs import checkpoint, abs_set, trigger_and_read, pause
from databroker import Broker

try:
  from ophyd.device import Kind
  from ophyd.ee_instruments import generate_ophyd_obj, BasicStatistics, \
      FilterStatistics, ManualDevice
except ModuleNotFoundError:
    print('Ophyd fork is not installed')
    print('First, (if needed) uninstall base ophyd:')
    print('  $ python -m pip uninstall ophyd')
    print('Next, install the fork:')
    print('  $ python -m pip install git+https://github.com/lucask07/ophyd@master#egg=ophyd')

from instrbuilder.instrument_opening import open_by_name
from instrbuilder.instruments import create_ada2200


RE = RunEngine({})
db = Broker.named('local_file')  # a broker poses queries for saved data sets
# Insert all metadata/data captured into db.
RE.subscribe(db.insert)

# ------------------------------------------------
#           Multimeter
# ------------------------------------------------
scpi_dmm = open_by_name(name='my_multi')
scpi_dmm.name = 'dmm'
DMM, component_dict = generate_ophyd_obj(name='Multimeter', scpi_obj=scpi_dmm)
dmm = DMM(name='multimeter')

# configure for fast burst reads
dmm.volt_autozero_dc.set(0)
dmm.volt_aperture.set(20e-6)
dmm.volt_range_auto_dc.set(0)  # turn off auto-range
dmm.volt_range_dc.set(10)      # set range

# create an object that returns statistics calculated on the arrays returned by read_buffer
# the name is derived from the parent
# (e.g. lockin and from the signal that returns an array e.g. read_buffer)
dmm_burst_stats = BasicStatistics(name='', array_source=dmm.burst_volt_timer)
dmm_filter_stats = FilterStatistics(name='', array_source=dmm.burst_volt_timer)

# ------------------------------------------------
#           Power Supply
# ------------------------------------------------
scpi_pwr = open_by_name(name='rigol_pwr1')
scpi_pwr.name = 'pwr'
PWR, component_dict = generate_ophyd_obj(name='pwr_supply', scpi_obj=scpi_pwr)
pwr = PWR(name='pwr_supply')

# disable outputs
pwr.out_state_chan1.set('OFF')
pwr.out_state_chan2.set('OFF')
pwr.out_state_chan3.set('OFF')

# over-current
pwr.ocp_chan1.set(0.06)
pwr.ocp_chan2.set(0.06)
pwr.ocp_chan3.set(0.06)

# over-voltage
pwr.ovp_chan1.set(3)
pwr.ovp_chan2.set(3)
pwr.ovp_chan3.set(5.5)

# voltage
pwr.v_chan1.set(2.5)  # split rails (-2.5 V)
pwr.v_chan2.set(2.5)  # split rails (2.5 V)
pwr.v_chan3.set(5)    # single supply (5 V)

# current
pwr.i_chan1.set(0.04)
pwr.i_chan2.set(0.04)
pwr.i_chan3.set(0.04)

# enable outputs
pwr.out_state_chan1.set('ON')
pwr.out_state_chan2.set('ON')
pwr.out_state_chan3.set('ON')

# ------------------------------------------------
#           ADA2200 SPI Control with Aardvark
# ------------------------------------------------
ada2200_scpi = create_ada2200()
SPI, component_dict = generate_ophyd_obj(name='ada2200_spi', scpi_obj=ada2200_scpi)
ada2200 = SPI(name='ada2200')

ada2200.serial_interface.set(0x10)  # enables SDO (bit 4,3 = 1)
ada2200.demod_control.set(0x18)     # bit 3: 0 = SDO to RCLK
ada2200.analog_pin.set(0x02)        # extra 6 dB of gain for single-ended inputs
ada2200.clock_config.set(0x06)      # divide input clk by x16

# ------------------------------------------------
#           Function Generator
# ------------------------------------------------
fg_scpi = open_by_name(name='new_function_gen')   # name within the configuration file (config.yaml)
fg_scpi.name = 'fg'
FG, component_dict = generate_ophyd_obj(name='fg', scpi_obj=fg_scpi)
fg = FG(name='fg')

if fg.unconnected:
    sys.exit('Function Generator is not connected, exiting blueksy demo')
RE.md['fg'] = fg.id.get()

# setup control of the frequency sweep
tau = 10e-3
fg.freq.delay = tau * 9
test_frequency = 390.58

# configure the function generator
fg.reset.set(None)  # start fresh
fg.function.set('SQU')
fg.load.set(50)
fg.freq.set(test_frequency)
fg.v.set(2e-3)  #
fg.freq.set(0.00001)
fg.offset.set(0)
fg.output.set('ON')

dmm.burst_volt_timer.stage()
time.sleep(0.1)

# --------------------------------------------------------
#                   Get a baseline with averaging
# --------------------------------------------------------
dets = [dmm.burst_volt_timer,
        dmm_burst_stats.mean,
        dmm_filter_stats.filter_6dB_mean,
        dmm_filter_stats.filter_6dB_std,
        dmm_filter_stats.filter_24dB_mean,
        dmm_filter_stats.filter_24dB_std]

# shorten names for the LiveTable
dmm_burst_stats.mean.name = 'mean'
dmm_filter_stats.filter_6dB_mean.name = 'filter_6dB_mean'
dmm_filter_stats.filter_6dB_std.name = 'filter_6dB_std'
dmm_filter_stats.filter_24dB_mean.name = 'filter_24dB_mean'
dmm_filter_stats.filter_24dB_std.name = 'filter_24dB_std'

# prime the statistics measurements with a trigger, otherwise 'describe' fails due to
#  None type
for det in dets:
    det.trigger()

input('50 Ohm attenuators only. Resume?')
uid_offset = RE(count(dets,
                      num=5, delay=0.2),
                      LiveTable(dets),
                      # input parameters below are added to metadata
                      attenuator='50OhmTerm',
                      purpose='offset_ADA2200',
                      operator='Lucas',
                      dut='ADA2200',
                      preamp='yes_AD8655',
                      notes='offset-no-inputs')

# baseline measurement
offset = db[uid_offset[0]].table()
measured_offset = np.mean(offset['filter_6dB_mean'])

print('Measured offset value of {}'.format(measured_offset))
input('Replace RCLK input, keep 50 Ohm on interferer: Resume?')


uid_baseline = RE(count(dets,
                        num=20, delay=0.2),
                        LiveTable(dets),
                        # input parameters below are added to metadata
                        attenuator='53dB',
                        purpose='dynamic_reserve_ADA2200',
                        operator='Lucas',
                        dut='ADA2200',
                        preamp='yes_AD8655',
                        notes='baseline-no-interferer')

# baseline measurement
baseline = db[uid_baseline[0]].table()
expected_value = np.mean(baseline['filter_6dB_mean'])

print('Measured expected value of {}'.format(expected_value))
input('Replace both inputs: Resume?')
# --------------------------------------------------------
#                   Run a 2D sweep of the FG2 frequency and amplitude
# --------------------------------------------------------


def calc_error_deviation(value, baseline_meas, measured_offset):
    return abs((value-baseline_meas)/(baseline_meas - measured_offset)*100)


calc_per_error = functools.partial(calc_error_deviation, baseline_meas=expected_value,
                                   measured_offset=measured_offset)


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
    Targets Dynamic Reserve testing

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

#  Construct frequency array to test over, specifically add harmonics
# freq_arr = np.logspace(1.8, 4.5, 40)  # 63 - 31622
freq_arr = np.logspace(1.4, 3.4, 40)  # 25.1 - 2511
# freq_arr = np.logspace(1.4, 3.4, 20)  # 25.1 - 2511
harmonic_multiplier = np.array([1, 0.998, 1.002, 1.03, 0.97, 1.01, 0.99])
# harmonic_multiplier = np.array([0.998, 1.002])

harmonics = [1/3, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9]
harmonics = [1/3, 0.5, 1, 2, 3, 4, 8]

# harmonics = [0.5, 1, 2]
# freq_arr = np.array([])

for hrm in harmonics:
    freq_arr = np.append(freq_arr, test_frequency*hrm*harmonic_multiplier)
freq_arr = np.sort(freq_arr)
print('Total number of points: {}'.format(len(freq_arr)))

fg.output.set('ON')
fg.freq.set(freq_arr[0])
time.sleep(tau*12)

# specific setup needed to read ADA2200 registers,
#  so do ahead of the experiment run, and then re-enable RCLK output
ada2200.serial_interface.set(0x18)  # enables SDO (bit 4,3 = 1)
ada2200.demod_control.set(0x10)  # SDO to RCLK
ada_config = ada2200.read_configuration()
ada2200.serial_interface.set(0x10)  # enables SDO (bit 4,3 = 1)
ada2200.demod_control.set(0x18)     # bit 3: 0 = SDO to RCLK

uid = RE(target_value(dets, 'filter_6dB_mean',
         motor=fg.v, start=0.01, stop=6.1,
         min_step=0.025, target_val=5,
         calc_function=calc_per_error, accuracy=50e-3,
         outer_motor=fg.freq, outer_steps=freq_arr),
         LiveTable(dets),
         # input parameters below are added to metadata
         attenuator_RCLK='53dB',
         attenuator_fg2='0dB',
         purpose='dynamic_reserve_ADA2200',
         operator='Lucas',
         dut='ADA2200',
         preamp='yes_AD8655',
         notes='modified setup and measured amp; switch to 50Ohm output for FGs',
         transfer_function_fg1='?',
         transfer_function_fg2='?',
         fg_config=fg.read_configuration(),
         ada2200_config=ada_config,
         dmm_config=dmm.read_configuration())

fg.output.set('OFF')

# # ------------------------------------------------
# #   	(briefly) Investigate the captured data
# # ------------------------------------------------
#
# # baseline measurement
# baseline = db[uid_baseline[0]].table()
# expected_value = np.mean(baseline['lockin_A'])
#
# get data into a pandas data-frame
header = db[uid[0]]  # db is a DataBroker instance
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
h = db[-1]
df_meta = h.table('baseline')

print('These configuration values are saved to baseline data:')
print(df_meta.columns.values)

import matplotlib.pyplot as plt
'''
for int_v in df['fgen2_v'].unique():
    idx = (df['fgen2_v'] == int_v)
    x = df.loc[idx]['fgen2_freq']
    y = (df.loc[idx]['lockin_A'] - expected_value)/expected_value*100
    plt.semilogx(x, y, marker='*', label='{:0.2f} V'.format(int_v))
plt.legend()
'''

plt.plot(df['fg_v'], df['filter_6dB_mean'], marker='*')

print('UID baseline = {}'.format(uid_baseline))
print('UID = {}'.format(uid))
