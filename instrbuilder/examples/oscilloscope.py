# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas


from instrument_opening import open_by_name
import time

osc = open_by_name(name='msox_scope')  # name within the configuration file (config.yaml)

osc.set('time_range', 1e-3)
osc.set('chan_scale', 0.8, configs={'channel': 1})
osc.set('chan_offset', -0.2, configs={'channel': 1})

osc.set('single_acq')
time.sleep(0.1)

# save a PNG screen-shot to host computer
t = osc.save_display_data('test')
