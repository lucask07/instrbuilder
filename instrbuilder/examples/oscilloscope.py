# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

from instrbuilder.instrument_opening import open_by_name
import time

KEYSIGHT = False
RIGOL = True

if KEYSIGHT:
	osc = open_by_name(name='msox_scope')  # name within the configuration file (config.yaml)

	osc.set('time_range', 1e-3)
	osc.set('chan_scale', 0.8, configs={'chan': 1})
	osc.set('chan_offset', -0.2, configs={'chan': 1})

	osc.set('single_acq')
	time.sleep(0.1)

	# save a PNG screen-shot to host computer
	t = osc.save_display_data('test')

if RIGOL:
	# rigol_ds is the name in my YAML file
	osc = open_by_name(name='rigol_ds')

	osc.set('time_range', 1e-3)
	osc.set('chan_scale', 0.8, configs={'chan': 1})
	osc.set('chan_offset', -0.2, configs={'chan': 1})

	osc.set('single_acq')
	time.sleep(0.1)

	# save a PNG screen-shot to host computer
	t = osc.save_display_data('test')

	osc.set('stop_acq')
	osc.set('run_acq')   

	# connect a fg to CHAN1: 400 mVpk-pk, 1kHz, high-z output
	time.sleep(2)
	osc.set('trigger_mode', 'EDGE')
	osc.set('trigger_sweep', 'NORM')
	osc.set('trigger_source', 1)   
	osc.set('trigger_level', 0.2)        

	time.sleep(2)

	# specific measure
	vp = osc.get('meas_vpp', configs={'chan':1})

	# general measure -- input measure type
	vavg = osc.get('meas', configs={'meas_type':'VAVG', 'chan':1}) 

	print('Measured pk-pk voltage of = {}'.format(vp))
	print('Measured avg voltage of = {}'.format(vavg))


