# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import visa
import oyaml as yaml  # oyaml preserves ordering
import os
import sys
import inspect

p = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(p)
from scpi import init_instrument
import instruments
from utils import find_visa_connected

# use symbolic links
sys.path.append(
    '/Users/koer2434/instrbuilder/')  # this instrbuilder: the SCPI library


def get_bit(value, bit):
    """ 
    Returns single bit from byte 

    Parameters
    ----------
    value : int    
    bit : int
        the bit position to determine value of 
    
    Returns
    -------
    0 or 1

    """
    bit_val = 1 if (value & 2**(bit) != 0) else 0
    return bit_val


def set_bit(value, bit):
    """ 
    Sets single bit of byte 

    Parameters
    ----------
    value : int    
    bit : int
        the bit position to determine set value of 
    
    Returns
    -------
    int with new value

    """
    return value | 2**bit


def clear_bit(value, bit):
    """ 
    Clears single bit of byte 

    Parameters
    ----------
    value : int    
    bit : int
        the bit position to clear value of 
    
    Returns
    -------
    int with new value

    """
    return value & ((2**8 - 1) - bit**2)


def find_visa_connected():
    """
    Finds VISA connected devices, returns the connected resources as a list 
    """

    mgr = visa.ResourceManager()
    resources = mgr.list_resources()
    print('Found VISA devices: ')
    print(resources)
    return resources


def find_instrument_classes():
    """
    Find the classes in instruments.py by name
        (to later instantiate use getattr: SRSLockIn = getattr(instruments, 'SRSLockIn') )

    Returns
    -------
    list
        List of classes in instruments.py by name
    """

    instrument_classes = []
    for name, obj in inspect.getmembers(instruments):
        if inspect.isclass(obj):
            # print(obj)
            # print(obj.__name__)
            instrument_classes.append(obj.__name__)

    return instrument_classes


def user_input(address, name=None, filename='config.yaml'):
    """
    Gather user input for adding an instrument to the YAML configuration file

    Parameters
    ----------
    address : dict
        The interface as dict key (i.e. 'pyvisa') and the address as the value
    name : str
        Instrument name (as the top node) used in the YAML

    Returns
    -------
    dict
        The configuration dictionary that will be used to append the YAML
    """
    # read current YAML
    yaml_config = open(filename, 'r')
    current_configs = yaml.safe_load(yaml_config)

    config = {'address': address}

    ok = False
    if name is None:
        while not ok:
            name = input('Enter your desired name for the instrument:')
            if len(name) == 0 or not isinstance(name, str):
                print('Bad input, try again')
            else:
                ok = True
    config[name] = {}

    # determine the class to assign
    instrument_classes = find_instrument_classes()
    print('What class to assign to this instrument?')
    for num, ic in enumerate(instrument_classes):
        print('({}) {}'.format(num, ic))
    class_num = int(input('  Enter the number associated with the class: '))
    if not isinstance(class_num, int) or (class_num > len(instrument_classes)):
        print('Bad selection of class')
        return {}
    config[name]['python_class'] = instrument_classes[class_num]

    # get location of CSV files
    print('The instrument command CSV files are within:\n  {}/'.format(configs['csv_directory']))
    print('Enter where (within the directory above) this instruments CSV files are')
    csv_loc = input('  An example is keysight/oscilloscope/MSOX3000 :    ')

    print(current_configs['csv_directory'])
    csv_dir = os.path.join(current_configs['csv_directory'], csv_loc)

    if not os.path.isdir(csv_dir):
        print('Directory {} does not exist. Exiting'.format(csv_dir))
        return {}
    config[name]['csv_folder'] = csv_loc

    return config


def append_to_yaml(new_configs, filename='config.yaml'):
    """
    Append to the configuration file (after some checking) and after copying to {name}_backup.yaml

    Parameters
    ----------
    new_configs : dict
        A new instrument configuration as a dict. Should not have the key 'instruments' (i.e. lower in the tree)
    filename : str (optional)
        The name of the YAML configuration file

    Returns
    -------
    None

    """

    # read current YAML
    yaml_config = open(filename, 'r')
    configs = yaml.safe_load(yaml_config)

    if 'instruments' in new_configs.keys():
        print('Error: instruments key is in the new configuration dictionary')
        return

    # copy YAML
    os.rename(filename, filename.replace('.yaml', '_backup.yaml'))

    # append new dictionary to old dictionary
    configs['instruments'].update(new_configs)

    # write to YAML file
    with open(filename, 'w+') as f:
        # see: https://pyyaml.org/wiki/PyYAMLDocumentation (for default_flow_style)
        yaml.dump(configs, f, default_flow_style=False)
    return


def detect_instruments(filename='config.yaml'):
    """
    Detect PyVISA instruments connected to the computer and return their addresses.

    Returns
    -------
    (list, list):
        a list of all PyVISA addresses found
        a list of all PyVISA addresses found that are not in the config file
    """

    yaml_config = open(filename, 'r')
    configs = yaml.safe_load(yaml_config)

    device_addrs = find_visa_connected()
    usb_addrs = [k for k in device_addrs if 'USB0' in k]

    for addr in usb_addr:
        mgr = visa.ResourceManager()
        obj = mgr.open_resource(addr)
        try:
            res = obj.query('*IDN?')
            print('-'*40)
            print('Instrument address {}:'.format(addr))
            print(res.strip('\n'))
        except Exception as e:
            print('ID failed on address: {}'.format(addr))
            print(e)
        obj.close()
    print('-' * 40)

    # create list of the PyVISA addresses tracked in the config file
    config_addr = [configs['instruments'][k]['addr'] for k in configs['instruments']]

    interface = 'pyvsia'
    pyvisa_addr = [c[interface] for c in config_addr if interface in c]

    interface = 'pyserial'
    pyserial_addr = [c[interface] for c in config_addr if interface in c]

    # look for instruments that are not in the configuration file
    not_in_config = []
    for addr in usb_addrs:
        if addr not in pyvisa_addr:
            print('Addr: {} is not in your system configuration file.\n Should we add it?'.format(addr))
            not_in_config.append(addr)

    return usb_addrs, not_in_config
