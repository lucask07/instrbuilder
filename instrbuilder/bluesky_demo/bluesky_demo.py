# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports
import sys
import os
import time

# imports that may need installation
import matplotlib.pyplot as plt
from bluesky import RunEngine
from bluesky.callbacks import LiveTable, LivePlot
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import scan, grid_scan
from databroker import Broker

# use symbolic links
sys.path.append('/Users/koer2434/ophyd/ophyd/')
sys.path.append(
    '/Users/koer2434/instrbuilder/')

# imports that require sys.path.append pointers
from ophyd.device import Kind
from ophyd.ee_instruments import LockInAuto, FunctionGenAuto
import scpi

base_dir = os.path.abspath(
    os.path.join(os.path.dirname(scpi.__file__), os.path.pardir))

RE = RunEngine({})
bec = BestEffortCallback()
# Send all metadata/data captured to the BestEffortCallback.
# RE.subscribe(bec) # in this demo we will explicitly define LiveTables and Plots

db = Broker.named('local_file')  # a broker poses queries for saved data sets

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)

lia = LockInAuto(name='lia')
if lia.unconnected:
    sys.exit('LockIn amplifier is not connected, exiting blueksy demo')
lia.reset.set(0)
RE.md['lock_in'] = lia.id.get()

# -------------------------------------
#					Function Generator
# ------------------------------

fg = FunctionGenAuto(name='fg')
if fg.unconnected:
    sys.exit('Function Generator is not connected, exiting blueksy demo')
RE.md['lock_in'] = fg.id.get()

# setup control of the frequency sweep
fg.freq.delay = 0.2
fg.freq.kind = Kind.hinted

# TODO: Best methods to read configurations?
#       1) as below, append to supplemental data: to SQL
#       2) assign a metadata parameter to instrument.read_configuration(): to JSON
#       3) both?: means read twice
#       4) the answer might be the following: if the information is used in data analysis put in the SQL
#                                             if the information is used to sort files, etc. put into JSON

############# ------------------------------ #############
#					Setup Supplemental Data				 #
############# ------------------------------ #############
from bluesky.preprocessors import SupplementalData
baseline_dets = []
for dev in [fg, lia]:
    for name in dev.component_names:
        if getattr(dev, name).kind == Kind.config:
            baseline_dets.append(getattr(dev, name))

sd = SupplementalData(baseline=baseline_dets, monitors=[], flyers=[])
RE.preprocessors.append(sd)

############# ------------------------------ #############
#					Run a measurement					 #
############# ------------------------------ #############

for i in range(1):
    # scan is a pre-configured Bluesky plan; returns the experiment uid
    uid = RE(
        scan([lia.disp_val], fg.freq, 4997, 5005, 8),
        LiveTable([fg.freq, lia.disp_val]),
        # the input parameters below will be metadata
        attenuator='60dB',
        purpose='demo',
        operator='Lucas',
        fg_config=fg.read_configuration(),
        lia_config=lia.read_configuration())
if 0:
    ############# ------------------------------ #############
    #                   Run a 2D sweep                       #
    ############# ------------------------------ #############
    # setup control of the lock-in filter-slope sweep
    lia.filt_slope.delay = 2
    lia.filt_slope.kind = Kind.hinted
    # ToDo: pass datatypes to bluesky automatically
    lia.filt_slope.dtype = 'string' 

    if len(addr) != 0:
        for i in range(1):
            # grid_scan is a pre-configured Bluesky plan; returns the experiment uid
            uid = RE(
                grid_scan([lia.disp_val], 
                    lia.filt_slope, 0, 3, 4,
                    fg.freq, 4997, 5005, 30, False),
                # LiveTable([lia.disp_val]),
                LivePlot('disp_val', 'freq'),
                # the input parameters below will be metadata
                attenuator='60dB',
                purpose='demo',
                operator='Lucas',
                fg_config=fg.read_configuration(),
                lia_config=lia.read_configuration())
            # TODO: the name of the SCPI command becomes the display name used by bluesky,
            #        would like to be able to rename the plot axis

# ------------------------------
#				Example Data Processing
# ------------------------------

# get data into a pandas data-frame
header = db[uid[0]]  # db is a DataBroker instance
print(header.table())
df = header.table()
# view the baseline data (i.e. configuration values)
h = db[-1]
h.table('baseline')

if 0:
    plt.figure()
    for fs in df['filt_slope'].unique():
        idx = (df['filt_slope'] == fs)
        plt.plot(df.loc[idx]['freq'], df.loc[idx]['disp_val'],
            marker = '*',
            label = 'Filt. slope = {}'.format(fs))
    plt.legend()
    # metadata
    header['start']
    header['stop']

    # view the baseline data (i.e. configuration values)
    h = db[-1]
    h.table('baseline')

    lia.read_buffer.unstage()
    lia.read_buffer.stage()
    print('Starting scan')
    lia.read_buffer.trigger()
    time.sleep(0.2)
    uid = RE(scan([lia.read_buffer, lia.isum],
                    fg.freq, 4997, 5005, 12),
                LiveTable([fg.freq, lia.read_buffer, lia.isum]),
                # the input parameters below will be metadata
                attenuator='60dB',
                purpose='demo',
                operator='Lucas')