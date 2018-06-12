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

# use symbolic links
sys.path.append(
    '/Users/koer2434/ophyd/')  # these 2 will become an import of ophyd
sys.path.append('/Users/koer2434/ophyd/ophyd/')  #
sys.path.append(
    '/Users/koer2434/instrbuilder/')  # this instrbuilder: the SCPI library

# imports that require sys.path.append pointers
from ophyd.signal import ScpiSignal, ScpiSignalBase
from ophyd import Device, Component
from ophyd.device import Kind
from scpi import init_instrument, SCPI
from instruments import SRSLockIn, AgilentFunctionGen
import scpi

base_dir = os.path.abspath(
    os.path.join(os.path.dirname(scpi.__file__), os.path.pardir))

plt.close('all')

RE = RunEngine({})
bec = BestEffortCallback()
# Send all metadata/data captured to the BestEffortCallback.
RE.subscribe(bec)
db = Broker.named('local_file')  # a broker poses queries for saved data sets

# Insert all metadata/data captured into db.
RE.subscribe(db.insert)

############# ------------------------------ #############
#					Lock-in Amplifier 					 #
############# ------------------------------ #############
# get lockin amplifier SCPI object
instrument_path = 'instruments/srs/lock_in/sr810/'
cmd_name = 'commands.csv'
lookup_name = 'lookup.csv'
cmd_map = os.path.join(base_dir, instrument_path, cmd_name)
lookup_file = os.path.join(base_dir, instrument_path, lookup_name)
addr = {'pyserial': '/dev/tty.USA19H14512434P1.1'}

# addr = {} # an empty address dictionary will return an unconnected instrument
cmd_list, inst_comm, unconnected = init_instrument(
    cmd_map, addr=addr, lookup=lookup_file, init_write='OUTX 0')
lia = SRSLockIn(cmd_list, inst_comm, name='lock-in', unconnected=unconnected)
# reset the lockin amplifier
lia.set(0, 'reset')

# Immediately add the lock-in instrument id to the run-engine metadata
RE.md['lock_in'] = lia.vendor_id


# create a Bluesky Lock-in device
class LockIn(Device):
    fmode = Component(ScpiSignal, scpi_cl=lia, cmd_name='fmode', configs={})
    tau = Component(ScpiSignal, scpi_cl=lia, cmd_name='tau', configs={})
    ch1_disp = Component(
        ScpiSignal, scpi_cl=lia, cmd_name='ch1_disp', configs={'ratio': 0})
    freq = Component(ScpiSignal, scpi_cl=lia, cmd_name='freq', configs={})
    disp_val = Component(
        ScpiSignal, scpi_cl=lia, cmd_name='disp_val', configs={})
    # Example of an Instrbuilder long setter, i.e. the SCPI command takes more than a single value
    off_exp = ScpiSignal(
        scpi_cl=lia, cmd_name='off_exp', configs={'chan':
                                                  2})  # offset and expand

    def stage(self):
        self.tau.set(8)
        self.fmode.set('Int')
        self.ch1_disp.set('X')  # magnitude
        self.freq.set(5e3)

    def unstage(self):
        pass


bsky_lia = LockIn(name='bsky_lia')

for cmpt in ['tau', 'fmode', 'freq']:
    setattr(getattr(bsky_lia, cmpt), 'kind', Kind.config)

############# ------------------------------ #############
#					Function Generator 					 #
############# ------------------------------ #############
instrument_path = 'instruments/agilent/function_gen/3320A/'
cmd_name = 'commands.csv'
lookup_name = 'lookup.csv'
cmd_map = os.path.join(base_dir, instrument_path, cmd_name)
lookup_file = os.path.join(base_dir, instrument_path, lookup_name)
addr = {'pyvisa': 'USB0::0x0957::0x0407::MY44060286::INSTR'}
# addr = {}
cmd_list, inst_comm, unconnected = init_instrument(
    cmd_map, addr=addr, lookup=lookup_file)
fg = AgilentFunctionGen(
    cmd_list, inst_comm, name='function-generator', unconnected=unconnected)

# Immediately add the function generator vendor/instrument_id to the run-engine metadata
RE.md['function_generator'] = fg.vendor_id


### -------- Example of a device: function generator ---------------
class FuncGen(Device):
    freq = Component(ScpiSignal, scpi_cl=fg, cmd_name='freq', configs={})
    v = Component(ScpiSignal, scpi_cl=fg, cmd_name='v', configs={})
    output = Component(ScpiSignal, scpi_cl=fg, cmd_name='output', configs={})
    offset = Component(ScpiSignal, scpi_cl=fg, cmd_name='offset', configs={})

    def stage(self):
        self.freq.set(4997)
        self.v.set(0.2)
        self.offset.set(0)
        if self.output.get() == 'OFF':
            self.output.set('ON')

    def unstage(self):
        # could/should turn the output off, but would rather not cycle the relay every time
        self.freq.set(4997)


bsky_fg = FuncGen(name='bsky_fg')

# setup control of the frequency sweep
bsky_fg.freq.delay = 0.2
bsky_fg.freq.kind = Kind.hinted

# TODO: bsky_rg.read_configuration() returns an empty OrderedDict if the configuration_attrs is simply populated
#		read_configuration() depends upon the setting of offset.kind for each component
#		should be = Kind.config
#		Am I doing something wrong or is the documentation stale?
for cmpt in ['output', 'v', 'offset']:
    setattr(getattr(bsky_fg, cmpt), 'kind', Kind.config)

############# ------------------------------ #############
#					Setup Supplemental Data				 #
############# ------------------------------ #############
from bluesky.preprocessors import SupplementalData
baseline_dets = []
for dev in [bsky_fg, bsky_lia]:
    for name in dev.component_names:
        if getattr(dev, name).kind == Kind.config:
            baseline_dets.append(getattr(dev, name))

sd = SupplementalData(baseline=baseline_dets, monitors=[], flyers=[])
RE.preprocessors.append(sd)

############# ------------------------------ #############
#					Run a measurement					 #
############# ------------------------------ #############

# stage the instrumetns
bsky_lia.stage()
bsky_fg.stage()

if len(addr) != 0:
    for i in range(1):
        # scan is a pre-configured Bluesky plan; returns the experiment uid
        uid = RE(
            scan([bsky_lia.disp_val], bsky_fg.freq, 4997, 5005, 12),
            LiveTable([bsky_lia.disp_val]),
            attenuator='0dB',
            purpose='demo',
            operator='Lucas',
            fg_config=bsky_fg.read_configuration(),
            lia_config=bsky_lia.read_configuration())
        # TODO: the name of the SCPI command becomes the display name used by bluesky,
        #		would like to be able to rename this

############# ------------------------------ #############
#				Example Data Processing					 #
############# ------------------------------ #############

if len(addr) != 0:
    # get data into a pandas dataframe
    header = db[uid[0]]
    print(header.table())
    df = header.table()
    plt.plot(df['freq'], df['disp_val'])
    # metadata
    header['start']
    header['stop']

    # view the baseline data
    h = db[-1]
    h.table('baseline')
