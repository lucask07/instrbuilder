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
from bluesky.preprocessors import fly_during_wrapper, fly_during_decorator
from databroker import Broker

sys.path.append('/Users/koer2434/Google Drive/UST/research/bluesky/new_ophyd/') # these 2 will become an import of my ophyd
sys.path.append('/Users/koer2434/Google Drive/UST/research/bluesky/new_ophyd/ophyd/') # 
sys.path.append('/Users/koer2434/Google Drive/UST/research/instrbuilder/instrbuilder/') # this will be the SCPI library

# imports that require sys.path.append pointers 
from ophyd.sim import det, flyer1, flyer2  # simulated hardware


RE = RunEngine({})
db = Broker.named('local_file') # a broker poses queries for saved data sets
bec = BestEffortCallback()
# Send all metadata/data captured to the BestEffortCallback.
RE.subscribe(bec)
db = Broker.named('local_file') # a broker poses queries for saved data sets

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)

# Define a new plan for future use.
RE(fly_during_wrapper(count([det], num=5), [flyer1, flyer2]))

# fly_and_count = fly_during_decorator([flyer1, flyer2])(count)
# RE(fly_and_count([det]))