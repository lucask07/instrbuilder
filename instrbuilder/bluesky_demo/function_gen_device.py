# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports
import sys

import yaml
import os
from scpi import init_instrument
from instruments import KeysightFunctionGen

# use symbolic links
sys.path.append('/Users/koer2434/ophyd/ophyd/')
sys.path.append(
    '/Users/koer2434/instrbuilder/')

# imports that require sys.path.append pointers
from ophyd.ee_instruments import FunctionGen, EEInstrument
from ophyd import Device
import scpi

yaml_config = open(os.path.join(os.path.dirname(scpi.__file__),
				   'config.yaml'), 'r')
configs = yaml.load(yaml_config)

base_dir = os.path.abspath(
    os.path.join(os.path.dirname(scpi.__file__), os.path.pardir))


# get lockin amplifier SCPI object
cmd_name = 'commands.csv'
lookup_name = 'lookup.csv'

# Function Generator 33500B SCPI object
instrument_path = 'instruments/keysight/function_gen/33500B/'
cmd_map = os.path.join(configs['base_directory'], instrument_path, cmd_name)
lookup_file = os.path.join(configs['base_directory'], instrument_path, lookup_name)
addr = {'pyvisa': 'USB0::0x0957::0x2B07::MY57700733::INSTR'}
cmd_list, inst_comm, unconnected = init_instrument(
    cmd_map, addr=addr, lookup=lookup_file)
scpi_fg = KeysightFunctionGen(
    cmd_list, inst_comm, name='function-generator', unconnected=unconnected)


#class MyFunctionGen(FunctionGen, EEInstrument, scpi=scpi_fg):
#    pass


class MyFunctionGen(FunctionGen, Device, scpi=scpi_fg):
    pass

""" This fails with:

---> 50 class MyFunctionGen(FunctionGen, Device, scpi=scpi_fg):
     51     pass
     52 

TypeError: __prepare__() got an unexpected keyword argument 'scpi'


__prepare__ is hit if inheriting from Device.  

"""

# get the bluesky FG
fg = MyFunctionGen()
"""

fg.reset.set(None)  # start fresh
fg.function.set('SIN')
fg.load.set('INF')
fg.freq.set(1220.680518480077)  # was 5e6/512/8
fg.v.set(2)  # full-scale range with 1 V RMS sensitivity is 2.8284
fg.offset.set(1.65)
fg.output.set('ON')
"""