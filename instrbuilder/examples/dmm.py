# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import yaml
import os
import sys
import wrapt 

print(__file__)
p = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
print(p)
sys.path.append(p)
from scpi import init_instrument
from instruments import KeysightMultimeter

# Bluesky stuff is temporary, until I figure out how to deal with getters that 
# 	return arrays or images 
from bluesky import RunEngine
from bluesky.callbacks import LiveTable, LivePlot
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import scan, count
from databroker import Broker

sys.path.append('/Users/koer2434/Google Drive/UST/research/bluesky/new_ophyd/') # these 2 will become an import of my ophyd
sys.path.append('/Users/koer2434/Google Drive/UST/research/bluesky/new_ophyd/ophyd/') # 
sys.path.append('/Users/koer2434/Google Drive/UST/research/instrbuilder/instrbuilder/') # this will be the SCPI library

# imports that require sys.path.append pointers 
from ophyd.signal import ScpiSignal, ScpiBaseSignal
from ophyd import Device
from ophyd.device import Kind

yaml_config = open('config.yaml', 'r')
configs = yaml.load(yaml_config)

# get multimeter SCPI object 
commands = 'commands.csv'
lookups = 'lookup.csv'

instrument = 'keysight/multimeter/34465A'
cmd_map = os.path.join(configs['base_directory'], configs['csv_directory'], 
						instrument, commands)
lookup_file = os.path.join(configs['base_directory'], configs['csv_directory'], 
						instrument, lookups)

'''
Find connected VISA devices 
'''
# import visa
# mgr = visa.ResourceManager()
# resources = mgr.list_resources()
# print(resources)

addr = {'pyvisa': 'USB0::0x2A8D::0x0101::MY57503303::INSTR'}
cmd_list, inst_comm, unconnected = init_instrument(cmd_map, addr = addr, lookup = lookup_file)
dmm = KeysightMultimeter(cmd_list, inst_comm, name = 'dmm', unconnected = unconnected)

dmm.save_hardcopy(filename = 'test88', filetype = 'png')

'''
@wrapt.decorator
def only_one_return(wrapped, instance, args, kwargs):
    return wrapped(*args, **kwargs)[0]
dmm.hardcopy_blueksy = only_one_return(dmm.hardcopy)
'''
v = ScpiBaseSignal(dmm, 'meas_volt', configs = {'ac_dc': 'DC'})

# dmm._cmds['hardcopy'].returns_image = True

# img = ScpiBaseSignal(dmm, 'hardcopy')
