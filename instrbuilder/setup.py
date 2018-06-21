import os
import scpi
from scpi import init_instrument
from instruments import SRSLockIn, AgilentFunctionGen

# general to instrbuilder package
# could be in CONFIG
cmd_name = 'commands.csv'
lookup_name = 'lookup.csv'
save_path = '/Users/koer2434/Google Drive/UST/research/bluesky/data'

# LOCKIN amplifier SCPI object
instrument_path = 'instruments/srs/lock_in/sr810/'
# could be in CONFIG
base_dir = os.path.abspath(
    os.path.join(os.path.dirname(scpi.__file__), os.path.pardir))
cmd_map = os.path.join(base_dir, instrument_path, cmd_name)
lookup_file = os.path.join(base_dir, instrument_path, lookup_name)
addr = {'pyserial': '/dev/tty.USA19H14512434P1.1'}
cmd_list, inst_comm, unconnected = init_instrument(
    cmd_map, addr=addr, lookup=lookup_file, init_write='OUTX 0')
scpi_lia = SRSLockIn(cmd_list, inst_comm, name='lock-in', unconnected=unconnected)

# Function Generator SCPI object
instrument_path = 'instruments/agilent/function_gen/3320A/'
cmd_map = os.path.join(base_dir, instrument_path, cmd_name)
lookup_file = os.path.join(base_dir, instrument_path, lookup_name)
addr = {'pyvisa': 'USB0::0x0957::0x0407::MY44060286::INSTR'}

cmd_list, inst_comm, unconnected = init_instrument(
    cmd_map, addr=addr, lookup=lookup_file)
scpi_fg = AgilentFunctionGen(
    cmd_list, inst_comm, name='function-generator', unconnected=unconnected)


class DataSave():
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

#TODO: file_type has no impact
data_save = DataSave(directory=save_path, file_type='.npy')