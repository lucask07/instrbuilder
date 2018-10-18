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


# ada2200.write()

# ada2200.ask()