# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas
import instrbuilder as instr
from instr.instrument_opening import open_by_name

dmm = open_by_name(name='my_multi')   # name within the configuration file (config.yaml)

v = dmm.get('meas_volt', configs={'ac_dc': 'DC'})
print('Measured voltage of {} [V]'.format(v))
dmm.save_hardcopy(filename='test55', filetype='png')

# certain commands fail during test_all, not due to communication errors but due to
# incompatible configurations
"""
test_results = dmm.test_all(
    skip_commands=['fetch', 'reset', 'initialize', 'hardcopy'])
"""

# Check the trigger source command 'trig_source'
print('Test trigger source:')
dmm.test_command('trig_source')
print('Communication register status: {}'.format(dmm.get('comm_error_details')))

# samples at 1 kHz with the 34465A
num_reads = 100
voltage_burst = dmm.burst_volt(reads_per_trigger=num_reads, aperture=200e-6)  # trigger count default is 1

print('Measured a {} length voltage burst'.format(len(voltage_burst)))

assert num_reads == len(voltage_burst), "Voltage burst length does not match number of reads"

dmm.set('reset')
dmm.set('clear_status')
