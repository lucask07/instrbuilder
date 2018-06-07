# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import yaml
import os
import sys

print(__file__)
p = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
print(p)
sys.path.append(p)
from scpi import init_instrument

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
dmm, dmm_comm = init_instrument(cmd_map, addr = addr, lookup = lookup_file)


