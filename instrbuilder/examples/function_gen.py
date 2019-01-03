# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

'''
Demonstrate the function generator within instrbuilder
As an example of the automated testing of the command lists run 'test_all'
'''
import instrbuilder as instr
from instr.instrument_opening import open_by_name

# fg = open_by_name(name='new_function_gen')   # name within the configuration file (config.yaml)
fg = open_by_name(name='old_fg')   # name within the configuration file (config.yaml)

fg.set('offset', 0.5)
fg.set('load', 'INF')

test_results = fg.test_all(skip_commands=[])
fg.set('reset')
fg.set('clear_status')
