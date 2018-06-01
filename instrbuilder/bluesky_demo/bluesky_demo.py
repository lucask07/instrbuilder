# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports 
import sys
import os
import functools
# imports that may need installation
import matplotlib.pyplot as plt
from bluesky import RunEngine
from bluesky.callbacks import LiveTable, LivePlot
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import scan, count
from databroker import Broker

sys.path.append('/Users/koer2434/Google Drive/UST/research/bluesky/my_ophyd/') # these 2 will become an import of my ophyd
sys.path.append('/Users/koer2434/Google Drive/UST/research/bluesky/my_ophyd/my_ophyd/') # 
sys.path.append('/Users/koer2434/Google Drive/UST/research/instrbuilder/instrbuilder/') # this will be the SCPI library

# imports that require sys.path.append pointers 
from my_ophyd.signal import ScpiSignal, ScpiBaseSignal
from my_ophyd import Device
from scpi import init_instrument

plt.close('all')

RE = RunEngine({})
bec = BestEffortCallback()
# Send all metadata/data captured to the BestEffortCallback.
RE.subscribe(bec)
db = Broker.named('local_file') # a broker poses queries for saved data sets

# prettry print json from terminal
# cat run_starts.json | json_pp

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)

# get lockin amplifier SCPI object 
cmd_map = '/Users/koer2434/Google Drive/UST/research/instrbuilder/instruments/srs810/commands.csv'
lookup_file = '/Users/koer2434/Google Drive/UST/research/instrbuilder/instruments/srs810/lookup.csv'
addr = {'pyserial': '/dev/tty.USA19H14112434P1.1'}
# addr = {}
lia, lia_serial = init_instrument(cmd_map, addr = addr,
	lookup = lookup_file, init_write = 'OUTX 0')

# Immediately add the lock-in instrument id to the run-engine metadata
RE.md['lock_in'] = lia.vendor_id

# TODO: Remove this hack. How to ensure the commands unconnected value works with the getter conversion
#		function
lia._cmds['ch1_disp']._unconnected_val = b'1,0\r'

# reset the lockin amplifier 
lia.set(0, 'reset')

# Configure the lock-in amplfier 
#	(TODO: setup the bluesky stage methods to do this)

# Set the display to show "R" -- magnitude
lia.set(value = 1, name = 'ch1_disp', configs = {'ratio': 0})
# Time-constant 
lia.set(8, 'tau')
# Internal frequency mode, 5 kHz 
lia.set(5e3, 'freq')
lia.set('Int', 'fmode')

cmd_map = '/Users/koer2434/Google Drive/UST/research/instrbuilder/instruments/fg_3320a/commands.csv'
lookup_file = '/Users/koer2434/Google Drive/UST/research/instrbuilder/instruments/fg_3320a/lookup.csv'
addr = {'pyvisa': 'USB0::0x0957::0x0407::MY44060286::INSTR'}
# addr = {}
fg, fg_usb = init_instrument(cmd_map, addr = addr,
		lookup = lookup_file)
# Immediately add the function generator instrument id to the run-engine metadata
RE.md['function_generator'] = fg.vendor_id

# TODO: use bluesky to setup this initialization? 
# initialize the function generator
fg.set(0, 'offset')
fg.set('INF', 'load')
fg.set(0.1, 'v')
if fg.get('output') == 'OFF':
	fg.set('ON', 'output')

# setup the Bluesky "motor"
freq_motor = ScpiSignal(fg, 'freq')
freq_motor.delay = 0.1

# Add the Bluesky "detector from the lock-in" 
det = ScpiBaseSignal(lia, 'disp_val')

# Add a few Bluesky "motors" for the lock-in that change configurations: 
filt_tau = ScpiSignal(lia, 'tau')
# Example of an Instrbuilder long setter, i.e. the SCPI command takes more than a single value 
off_exp = ScpiSignal(lia, 'off_exp', configs = {'chan': 2}) # offset and expand

if len(addr) != 0:
	for i in range(3):
		# scan is a pre-configured Bluesky plan; return the uid
		uid = RE(scan([det], freq_motor, 4997, 5005, 12), 
			LiveTable([det]), sample_id='A', purpose='calibration', operator='me')
	# get data into a pandas dataframe 
	header = db[uid[0]]
	print(header.table())
	df = header.table()
	plt.plot(df['freq'], df['disp_val'])
	# metadata 
	header['start']
	header['stop']

	# Save the data to two other formats: csv and hdf5
	#	ALTHOUGH this is not needed and the .sqlite is file is the most complete 
	# See: https://pandas.pydata.org/pandas-docs/stable/io.html
	data_dir = '/Users/koer2434/Google Drive/UST/research/instrbuilder/data'
	
	filename = 'test_data_{}.csv'.format(uid[0])
	fullfile = os.path.join(data_dir, filename)
	print('saving table as: {}'.format(filename))
	print(' to directory: {}'.format(data_dir))
	df.to_csv(fullfile)

	filename = 'test_data_{}.hdf'.format(uid[0])
	fullfile = os.path.join(data_dir, filename) #TODO: what does the hdf key do?
	print('saving table as: {}'.format(filename))
	print(' to directory: {}'.format(data_dir))
	df.to_hdf(fullfile, key = 'test_id')

	# the location of the data database and the json metadata files is set by the config file 'local_file'
	# 	db = Broker.named('local_file') 
	# this .yml config file (on my system) is at ~/.config/databroker
	# each run of the run-engine makes an sqlite data file; 
	# 	all JSON metadata/headers (start; stop; event_descriptors) are in the same .json file

### --------
## Baseline example: save and validate instrument configurations 
from bluesky.preprocessors import SupplementalData

config_getters = [c for c in lia._cmds if ((lia._cmds[c].is_config == True) and (lia._cmds[c].getter_inputs == 0))]
config_getters.remove('ch1_disp')

# TODO: fix this (bluesky doesn't know how to print an array)
# 		modify any baseline getters that return multiple values; 
# 		bluesky expects a single value 

baseline_dets = []
for name in config_getters:
	b_det = ScpiBaseSignal(lia, name)
	baseline_dets.append(b_det)

b_det = ScpiBaseSignal(lia, 'ch1_disp', shape = (2,), dtype = 'array')
baseline_dets.append(b_det)

# TODO -- monitors? something that throws interrupt with update? 
sd = SupplementalData(baseline= baseline_dets, monitors=[], flyers=[])
RE.preprocessors.append(sd)

for i in range(3):
	if i == 2:
		lia._cmds['fmode']._unconnected_val = 33
	uid = RE(scan([det], freq_motor, 4997, 5005, 12), 
		LiveTable([det]), sample_id='B', purpose='demo-baseline', operator='me')

# view the baseline data 
h = db[-1]
h.table('baseline')

class FGAmpFreq(Device):
    x = ScpiSignal(fg, 'freq')
    y = ScpiSignal(fg, 'v')

amp_f = FGAmpFreq(name = 'first_device')