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
from bluesky.plan_stubs import checkpoint, abs_set, trigger_and_read, pause
from databroker import Broker

from ophyd.device import Kind
from ophyd.ee_instruments import generate_ophyd_obj, BasicStatistics, \
    FilterStatistics, ManualDevice
from instrument_opening import open_by_name
from instruments import create_ada2200


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
scpi_dmm = open_by_name(name='my_multi')
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


# TODO
# add in 6dB of gain since single-ended input  -- DONE
# measure ada2200 offset, disable RCLK out? :   disable with ada2200.demod_control.set(0x10)
# adjust range of DMM based on input?           dmm.volt_range_dc.set(1)
# use the scope to quantify input :             amplitude, RMS, dc average (at Att = 0 dB)

# input at 0 dB : 2.71V Pk-pk, 1.6205 V avg over N-cycles; AC RMS 1.233
# input at 30 dB: 95 mV pk-pk, 1.6319 V avg over N-cycles; AC RMS 35.80
# input at 390.58 Hz (with divide x16 of input clock)
# ------------------------------------------------
#           Attenuator (must be manually changed)
# ------------------------------------------------
att = ManualDevice(name='att')


# ------------------------------------------------
#   Run a measurement (with a custom per step)
# ------------------------------------------------
def custom_step(detectors, motor, step):
    """
    Inner loop of a 1D step scan
    Modified the default function for ``per_step`` param in 1D plans.
    Add a pause to adjust the attenuator
    """
    yield from checkpoint()
    print('Set attenuator to {}'.format(step))

    # adjust DMM range
    if step < 12:
        yield from abs_set(dmm.volt_range_dc, 10)
    elif step < 30:
        yield from abs_set(dmm.volt_range_dc, 1)
    elif step >= 30:
        yield from abs_set(dmm.volt_range_dc, 0.1)

    yield from pause()

    yield from abs_set(motor, step, wait=True)
    return (yield from trigger_and_read(list(detectors) + [motor]))


# -----------------------------------------------------
#                   Run a Measurement: sweep FG phase
# ----------------------------------------------------
ada2200.serial_interface.set(0x18)  # enables SDO (bit 4,3 = 1)
ada2200.demod_control.set(0x10)  # SDO to RCLK
ada_config = ada2200.read_configuration()

ada2200.serial_interface.set(0x10)  # enables SDO (bit 4,3 = 1)
ada2200.demod_control.set(0x18)     # bit 3: 0 = SDO to RCLK
dmm_config = dmm.read_configuration()

dmm.burst_volt_timer.stage()
time.sleep(0.1)

print('starting plan!')

uid = RE(
    list_scan([dmm.burst_volt_timer, dmm_burst_stats.mean,
               dmm_filter_stats.filter_6dB_mean, dmm_filter_stats.filter_24dB_mean,
               dmm_filter_stats.filter_6dB_std, dmm_filter_stats.filter_24dB_std],
              att.val, [0, 6, 10, 20, 30, 40, 50, 60, 70, 90, 1000], per_step=custom_step),
    LiveTable([att.val, dmm.burst_volt_timer]),
    # the parameters below will be metadata
    attenuator='attenuator sweep',
    purpose='snr_ADA2200',
    operator='Lucas',
    dut='ADA2200',
    preamp='yes_AD8655',
    notes='SNR with RCLK as input; trigger DMM with RCLK; 1000 dB = terminated (50 Ohm) input; filter tau = 10e-3',
    pwr_config=pwr.read_configuration(),
    ada2200_config=ada_config,
    dmm_config=dmm_config
)

# the script does not continue along
print('finished plan!')
# ------------------------------------------------
#   	(briefly) Investigate the captured data
# ------------------------------------------------

# get data into a pandas data-frame
# uid = '7bf78db6-4953-4249-8918-614c903fa9c1'
# uid = '08e94fac-e1f0-4d7f-9146-2699b480c87a'
header = db[uid]  # db is a DataBroker instance
print(uid)
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
h = db[-1]
df_meta = h.table('baseline')
