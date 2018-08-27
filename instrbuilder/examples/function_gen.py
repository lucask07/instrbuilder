# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas


from instrument_opening import open_by_name

fg = open_by_name(name='old_fg')   # name within the configuration file (config.yaml)

fg.set('offset', 0.5)
fg.set('load', 'INF')

# if fg.get('output') == '0':
# 	fg.set('ON', 'output')

