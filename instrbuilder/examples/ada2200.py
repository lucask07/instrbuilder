# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import yaml
import os
import sys
import wrapt

# TODO remove this addpath
# p = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# sys.path.append(p)

from command import Register
from ic import IC
from ic import AA  # aardvark adapter

print('Running ADA2200 SPI example')
print('-'*40)

reg_map = {'serial_interface': 			0x0000,  #MSBs
           'chip_type': 				0x0006,
           'filter1':					0x0011,
           'analog_pin':				0x0028,
           'sync_control':				0x0029,
           'demod_control':				0x002A,
           'clock_config':				0x002B}

regs = []
for r in reg_map:
    regs.append(Register(name=r, address=reg_map[r],
                         read_write='R/W', is_config=True))

aardvark = AA()  # communication adapter
ada2200 = IC(regs, aardvark,
             interface='SPI', name='ADA2200')

ada2200.set('demod_control', 0x1A)
ada2200.set('demod_control', 0x12)

# ada2200.set('demod_control', 0x1D)   # sets VOCM to 1.2 V
ada2200.set('serial_interface', 0x18)  # enables SDO (bit 4,3 = 1)

# SPI reads work
demod_ctrl = ada2200.get('demod_control')

# Print the read-back. The first two bytes are 0s since that is when command/address is sent
print('Read from Demod Control: 0x{:02x}'.format(demod_ctrl))
