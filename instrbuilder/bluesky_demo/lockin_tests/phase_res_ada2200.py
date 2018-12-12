# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

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

from ophyd.device import Kind
from ophyd.ee_instruments import generate_ophyd_obj, BasicStatistics, \
    FilterStatistics, ManualDevice
from instrument_opening import open_by_name
from instruments import create_ada2200

RE = RunEngine({})
db = Broker.named('local_file')  # a broker poses queries for saved data sets

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)

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

# create an object that returns statistics calculated on the arrays returned by read_buffer
# the name is derived from the parent
#  (e.g. lockin and from the signal that returns an array e.g. read_buffer)
dmm_burst_stats = BasicStatistics(name='', array_source=dmm.burst_volt_timer)

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
#           Oscilloscope
# ------------------------------------------------
# Oscilloscope Channel 1 is RCLK from ADA2200
# Oscilloscope Channel 2 is Input Sinusoid from function generator

osc_scpi = open_by_name(name='msox_scope')  # name within the configuration file (config.yaml)
osc_scpi.name = 'scope'
OSC, component_dict = generate_ophyd_obj(name='osc', scpi_obj=osc_scpi)
osc = OSC(name='scope')

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
        # LiveTable([fg.phase, osc.meas_phase, dmm.burst_volt_timer, dmm_burst_stats.mean]),
        LiveTable([fg.phase, osc.meas_phase, dmm.burst_volt_timer]),
        # the parameters below will be metadata
        attenuator='0dB',
        purpose='phase_dependence',
        operator='Lucas',
        dut='ADA2200',
        preamp='yes_AD8655')

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
