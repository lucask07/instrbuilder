# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import yaml
import os
import sys
import time

p = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(p)
from scpi import init_instrument
from instruments import KeysightMSOX3000
from utils import find_visa_connected

# use symbolic links
sys.path.append(
    '/Users/koer2434/instrbuilder/')  # this instrbuilder: the SCPI library

yaml_config = open('config.yaml', 'r')
configs = yaml.load(yaml_config)

# get multimeter SCPI object
cmd_name = 'commands.csv'
lookup_name = 'lookup.csv'

# example of using find_visa_connected to determine address(es)
connected_instr = find_visa_connected()
print(connected_instr)

# Multimeter SCPI object
instrument_path = 'instruments/keysight/oscilloscope/MSOX3000'
cmd_map = os.path.join(configs['base_directory'], instrument_path, cmd_name)
lookup_file = os.path.join(configs['base_directory'], instrument_path, lookup_name)

addr = {'pyvisa': 'USB0::0x0957::0x17A9::MY52160418::INSTR'}
cmd_list, inst_comm, unconnected = init_instrument(
    cmd_map, addr=addr, lookup=lookup_file)
osc = KeysightMSOX3000(
    cmd_list, inst_comm, name='osc', unconnected=unconnected)

osc.set('time_range', 1e-3, )
osc.set('chan_scale', 0.8, configs={'channel': 1})
osc.set('chan_offset', -0.2, configs={'channel': 1})
osc.set('chan_offset', 0.2, configs={'channel': 1})
osc.set('single_acq')

time.sleep(0.1)
t = osc.save_display_data('test')
