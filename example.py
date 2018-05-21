from scpi import init_instrument

use_serial = False
use_usb = False

# get lockin amplifier SCPI object 
cmd_map = 'instruments/srs810/commands.csv'
lookup = 'instruments/srs810/lookup.csv'

lockin_addr = '/dev/tty.USA19H14112434P1.1'
lia, lia_serial = init_instrument(cmd_map, use_serial = use_serial, 
					use_usb = False, addr = lockin_addr, lookup = lookup)

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

