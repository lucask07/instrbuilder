# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import yaml
import os
from scpi import init_instrument
from instruments import SRSLockIn

yaml_config = open('config.yaml', 'r')
configs = yaml.load(yaml_config)

# get lockin amplifier SCPI object 
cmd_name = 'commands.csv'
lookup_name = 'lookup.csv'

# LOCKIN amplifier SCPI object
instrument_path = 'instruments/srs/lock_in/sr810/'
cmd_map = os.path.join(configs['base_directory'], instrument_path, cmd_name)
lookup_file = os.path.join(configs['base_directory'], instrument_path, lookup_name)
addr = {'pyserial': '/dev/tty.USA19H14112434P1.1'}
cmd_list, inst_comm, unconnected = init_instrument(
    cmd_map, addr=addr, lookup=lookup_file, init_write='OUTX 0')
lia = SRSLockIn(cmd_list, inst_comm, name='lock-in', unconnected=unconnected)

print()
lia.get('phase')
lia.set('phase', 0.1)

print()
lia.help('phase')
print()


# A more complex Lock-in Amplifier set; requires input dictionary configs 
# Set the display to show "R" -- magnitude
lia.set(value = 1, name = 'ch1_disp', configs = {'ratio': 0})


