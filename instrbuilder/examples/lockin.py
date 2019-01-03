# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

from instrbuilder.instrument_opening import open_by_name

print('Warning ... The address to the serial adapter \n (E.g. /dev/tty.USA19H141113P1.1) can change ')
lia = open_by_name(name='srs_lockin')   # name within the configuration file (config.yaml)

print()
lia.get('phase')
lia.set('phase', 0.1)

print()
lia.help('phase')
print()

# A more complex Lock-in Amplifier set; requires input dictionary configs 
# Set the display to show "R" -- magnitude
lia.set(name='ch1_disp', value=1, configs={'ratio': 0})

# Read the value of the display
disp_val = lia.get('disp_val')
print('Value of the display = {}'.format(disp_val))