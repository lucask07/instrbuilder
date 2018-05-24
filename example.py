# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import yaml
import os
from scpi import init_instrument

yaml_config = open('config.yaml', 'r')
configs = yaml.load(yaml_config)

use_serial = True
use_usb = False

# get lockin amplifier SCPI object 
commands = 'commands.csv'
lookups = 'lookup.csv'

instrument = 'srs810'
cmd_map = os.path.join(configs['base_directory'], configs['csv_directory'], 
						instrument, commands)
lookup_file = os.path.join(configs['base_directory'], configs['csv_directory'], 
						instrument, lookups)

lockin_addr = '/dev/tty.USA19H14112434P1.1'
lia, lia_serial = init_instrument(cmd_map, use_serial = use_serial, 
					use_usb = False, addr = lockin_addr, lookup = lookup_file, init_write = 'OUTX 0')

print()
lia.get('phase')
lia.set(0.1, 'phase')

print()
lia.help('phase')
print()

# A more complex Lock-in Amplifier set; requires input dictionary configs 
# Set the display to show "R" -- magnitude
lia.set(value = 1, name = 'ch1_disp', configs = {'ratio': 0})


## Function generator 

# cmd_map = 'instruments/fg_3320a/commands.csv'
# fg_addr = 'USB0::0x0957::0x0407::MY44060286::INSTR'
# fg, fg_usb = init_instrument(cmd_map, use_serial = False, use_usb = use_usb, addr = fg_addr)

# fg.set(0, 'offset')
# fg.set('INF', 'load')

# if fg.get('output') == '0':
# 	fg.set('ON', 'output')

