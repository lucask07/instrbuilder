# Lucas J. Koerner
# 10/2021
# koerner.lucas@stthomas.edu
# University of St. Thomas

from instrbuilder.instrument_opening import open_by_name
print('Warning ... The address to the serial adapter \n (E.g. /dev/tty.USA19H141113P1.1) can change ')

# GW instek 6300 LCR meter
# need to pass in baudrate, reading eol, and writing terminator
# using a TrippLite USB to RS-232

lcr = open_by_name(name='gw_lcr', baudrate=115200, eol=b'\n', 
					terminator='')   # name within the configuration file (config.yaml)
lcr.get('freq')
lcr.set('freq', 100e3)