# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import yaml
import os
import sys
import wrapt

p = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(p)
from scpi import init_instrument
from instruments import KeysightMultimeter
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
instrument_path = 'instruments/keysight/multimeter/34465A'
cmd_map = os.path.join(configs['base_directory'], instrument_path, cmd_name)
lookup_file = os.path.join(configs['base_directory'], instrument_path, lookup_name)
addr = {'pyvisa': 'USB0::0x2A8D::0x0101::MY57503303::INSTR'}
cmd_list, inst_comm, unconnected = init_instrument(
    cmd_map, addr=addr, lookup=lookup_file)
dmm = KeysightMultimeter(
    cmd_list, inst_comm, name='dmm', unconnected=unconnected)


v = dmm.get('meas_volt', configs = {'ac_dc': 'DC'})
print('Measured voltage of {} [V]'.format(v))
dmm.save_hardcopy(filename='test55', filetype='png')

"""
test_results = dmm.test_all(
    skip_commands=['fetch', 'reset', 'initialize', 'hardcopy'])
"""
# certain commands will fail during test_all, not due to communication errors but do to
#	incompatible configurations

# Check the trigger source command 'trig_source'
print('------------------')
dmm.test_command('trig_source')
print(dmm.get('comm_error_details'))

# samples at 1 kHz with the 34465A 
voltage_burst = dmm.burst_volt(reads_per_trigger = 100, aperture = 200e-6)

x = dmm.burst_volt(reads_per_trigger = 1, aperture = 200e-6, 
					trig_source = 'EXT', trig_count = 1024, 
					volt_range = 10, trig_delay = 300e-6)

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)