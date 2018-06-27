# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import yaml
import os
from scpi import init_instrument
from instruments import KeysightFunctionGen


yaml_config = open('config.yaml', 'r')
configs = yaml.load(yaml_config)

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
fg = KeysightFunctionGen(
    cmd_list, inst_comm, name='function-generator', unconnected=unconnected)

# fg.set(0, 'offset')
# fg.set('INF', 'load')

# if fg.get('output') == '0':
# 	fg.set('ON', 'output')

