# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas
"""
Test SPI writes to the ADA2200 using an Aardvark adapter;
Verify by connecting multimeter to measure the voltage at VOCM
Must connect ADA2200 RCLK to Aardvark MISO (in order to verfiy readbacks)
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

from ophyd.device import Kind
from ophyd.ee_instruments import generate_ophyd_obj
from instrbuilder.instrument_opening import open_by_name

from instrbuilder.instruments import create_ada2200

# ------------------------------------------------
#           Multimeter
# ------------------------------------------------
scpi_dmm = open_by_name(name='my_multi')
DMM, component_dict = generate_ophyd_obj(name='Multimeter', scpi_obj=scpi_dmm)
dmm = DMM(name='multimeter')

# ------------------------------------------------
#           ADA2200 SPI Control with Aardvark
# ------------------------------------------------
ada2200_scpi = create_ada2200()
SPI, component_dict = generate_ophyd_obj(name='ada2200_spi', scpi_obj=ada2200_scpi)
ada2200 = SPI(name='ada2200')

ada2200.serial_interface.set(0x18)  # enables SDO (bit 4,3 = 1)
ada2200.demod_control.set(0x10)     # bit 3: 0 = SDO to RCLK

time.sleep(0.1)
v = dmm.meas_volt_dc.get()
print('Read VOCM of = {} [V]'.format(v))

ada2200.demod_control.set(0x15)   # sets VOCM to 1.2 V
time.sleep(0.1)
v = dmm.meas_volt_dc.get()
print('Read VOCM of = {} [V]'.format(v))

demod_ctrl = ada2200.demod_control.get()
print('Read back from ADA2200, demod_control = 0x{:02X}'.format(demod_ctrl))
