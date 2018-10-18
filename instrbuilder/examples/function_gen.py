# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

from instrument_opening import open_by_name

fg = open_by_name(name='new_function_gen')   # name within the configuration file (config.yaml)

fg.set('offset', 0.5)
fg.set('load', 'INF')

test_results = fg.test_all(skip_commands=[])
fg.set('reset')
fg.set('clear_status')
