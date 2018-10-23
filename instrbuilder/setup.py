import os
import scpi
from scpi import init_instrument
from instruments import SRSLockIn, AgilentFunctionGen, KeysightMultimeter, KeysightMSOX3000

# 8/24/2018, redo of config

# instruments have unique names stored in the system YAML file
# possible to open instrument by name (can over-write various parameters, e.g. serial address)
# if an instrument is found that is not in the system YAML file there is the possibly to add it
#   info when adding, instrument type -> specific SCPI class
# do more things silently: poll for serial addresses as well as pyvisa USB addresses
# can the YAML make a dictionary? 

# check what's connected vs. what's in YAML
# user must at least open by name since the user should pick the object variable name 

# detect instruments 
    # needs a list of interfaces 

# API:
#   def detect_instruments(optional config_file)
        # how does this do pyvisa vs. pyserial?
#   def update_config()
        # open as SCPI, get ID and close? [this works]
#   def add_toconfig(addr):
        # prompt the user for name
        # present the user with a list of available classes
        
#
# # general to instrbuilder package
# # could be in CONFIG
# cmd_name = 'commands.csv'
# lookup_name = 'lookup.csv'
save_path = '/Users/koer2434/Google Drive/UST/research/bluesky/data'
# base_dir = os.path.abspath(
#     os.path.join(os.path.dirname(scpi.__file__), os.path.pardir))
#
#
# # LOCKIN amplifier SCPI object
# instrument_path = 'instruments/srs/lock_in/sr810/'
# # could be in CONFIG
# cmd_map = os.path.join(base_dir, instrument_path, cmd_name)
# lookup_file = os.path.join(base_dir, instrument_path, lookup_name)
# addr = {'pyserial': '/dev/tty.USA19H141113P1.1'}
# # addr = {'unconnected': None}
# cmd_list, inst_comm, unconnected = init_instrument(
#     cmd_map, addr=addr, lookup=lookup_file, init_write='OUTX 0')
# scpi_lia = SRSLockIn(cmd_list, inst_comm, name='lockin', unconnected=unconnected)
#
# # Function Generator 3320A SCPI object
# instrument_path = 'instruments/agilent/function_gen/3320A/'
# cmd_map = os.path.join(base_dir, instrument_path, cmd_name)
# lookup_file = os.path.join(base_dir, instrument_path, lookup_name)
# addr = {'pyvisa': 'USB0::0x0957::0x0407::MY44060286::INSTR'}
# cmd_list, inst_comm, unconnected = init_instrument(
#     cmd_map, addr=addr, lookup=lookup_file)
# scpi_fg2 = AgilentFunctionGen(
#     cmd_list, inst_comm, name='fgen2', unconnected=unconnected)
#
#
# # Function Generator 33500B SCPI object
# instrument_path = 'instruments/keysight/function_gen/33500B/'
# cmd_map = os.path.join(base_dir, instrument_path, cmd_name)
# lookup_file = os.path.join(base_dir, instrument_path, lookup_name)
# addr = {'pyvisa': 'USB0::0x0957::0x2B07::MY57700733::INSTR'}
# cmd_list, inst_comm, unconnected = init_instrument(
#     cmd_map, addr=addr, lookup=lookup_file)
# scpi_fg = AgilentFunctionGen(
#     cmd_list, inst_comm, name='fgen', unconnected=unconnected)
#
# # Multimeter SCPI object
# instrument_path = 'instruments/keysight/multimeter/34465A'
# cmd_map = os.path.join(base_dir, instrument_path, cmd_name)
# lookup_file = os.path.join(base_dir, instrument_path, lookup_name)
# # hard-code the address in case more instruments are connected
# addr = {'pyvisa': 'USB0::0x2A8D::0x0101::MY57503303::INSTR'}
# cmd_list, inst_comm, unconnected = init_instrument(
#     cmd_map, addr=addr, lookup=lookup_file)
# scpi_dmm = KeysightMultimeter(
#     cmd_list, inst_comm, name='dmm', unconnected=unconnected)
#
# # Keysight Oscilloscope MSOX3012A
# instrument_path = 'instruments/keysight/oscilloscope/MSOX3000'
# cmd_map = os.path.join(base_dir, instrument_path, cmd_name)
# lookup_file = os.path.join(base_dir, instrument_path, lookup_name)
# addr = {'pyvisa': 'USB0::0x0957::0x17A9::MY52160418::INSTR'}
# cmd_list, inst_comm, unconnected = init_instrument(
#     cmd_map, addr=addr, lookup=lookup_file)
# print('Oscilloscope unconnected = {}'.format(unconnected))
# scpi_osc = KeysightMSOX3000(
#     cmd_list, inst_comm, name='osc', unconnected=unconnected)


class DataSave():
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

#TODO: file_type has no impact
data_save = DataSave(directory=save_path, file_type='.npy')