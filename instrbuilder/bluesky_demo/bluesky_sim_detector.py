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
import numpy as np

from bluesky import RunEngine
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import scan, count
from databroker import Broker

sys.path.append('/Users/koer2434/Google Drive/UST/research/bluesky/new_ophyd/') # these 2 will become an import of my ophyd
sys.path.append('/Users/koer2434/Google Drive/UST/research/bluesky/new_ophyd/ophyd/') # 
sys.path.append('/Users/koer2434/Google Drive/UST/research/instrbuilder/instrbuilder/') # this will be the SCPI library

# imports that require sys.path.append pointers 
from ophyd.sim import det, ab_det, cam_img, img_stats # simulated hardware
from ophyd.device import Device, Component

RE = RunEngine({})
db = Broker.named('local_file') # a broker poses queries for saved data sets
bec = BestEffortCallback()
# Send all metadata/data captured to the BestEffortCallback.
RE.subscribe(bec)

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)

# cam_img is a Camera device with file saving 
# img_stats is a signal that calculates stats from the cam_img image (2d array) 
RE(count([det, ab_det, cam_img, img_stats], num=5))

# TODO: fix 'cam_w_stats' -> Device 
#		and then expand the stats calculator to accept a list of functions/names
# RE(count([det, ab_det, cam_w_stats], num=5))

# Check that the stats calculation matches up if we load the file and re-calculate 
print('Verify that stats calculated match the ')
header = db[-1]
df = header.table()

save_path = '/Users/koer2434/Google Drive/UST/research/bluesky/data'
for index, row in df.iterrows():
	fname = row['cam_img']
	open_f = fname.replace('/', '_0_')
	open_f = open_f + '.npy'
	d = np.load(os.path.join(save_path, open_f))
	print('File Calculation = {}; Bluesky Calculation = {}'.format(np.sum(d), row['camera_sum']))


