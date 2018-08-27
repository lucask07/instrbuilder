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

# use symbolic links
sys.path.append(
    '/Users/koer2434/instrbuilder/')  # this instrbuilder: the SCPI library
home = os.path.join(os.path.expanduser("~"), '.instrbuilder')


def find_visa_connected():
    """
    Finds VISA connected devices, returns the connected resources as a list

    Returns
    -------
    tuple
        Tuple of the connected resources (by address)
    """

    mgr = visa.ResourceManager()
    resources = mgr.list_resources()
    print('Found VISA devices: ')
    for d in resources:
        if 'USB0' in d:
            print(d)
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


def user_input(address, interface=None, name=None, filename='config.yaml'):
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
    yaml_config = open(os.path.join(home, filename), 'r')
    current_configs = yaml.safe_load(yaml_config)

    ok = False
    if name is None:
        while not ok:
            name = input('Enter your desired name for the instrument:')
            if len(name) == 0 or not isinstance(name, str):
                print('Bad input, try again')
            else:
                ok = True

    config = {name: {}}

    if interface is None:
        interface = 'pyvisa'
    config[name] = {'address': {interface: address}}

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
    print('The instrument command CSV files are within:\n  {}/'.format(current_configs['csv_directory']))
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
    yaml_config = open(os.path.join(home, filename), 'r')
    configs = yaml.safe_load(yaml_config)

    if 'instruments' in new_configs.keys():
        print('Error: instruments key is in the new configuration dictionary')
        return

    # copy YAML
    os.rename(os.path.join(home, filename), os.path.join(home, filename).replace('.yaml', '_backup.yaml'))

    # append new dictionary to old dictionary
    configs['instruments'].update(new_configs)

    # write to YAML file
    with open(os.path.join(home, filename), 'w+') as f:
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

    yaml_config = open(os.path.join(home, filename), 'r')
    configs = yaml.safe_load(yaml_config)

    device_addrs = find_visa_connected()
    usb_addrs = [k for k in device_addrs if 'USB0' in k]

    for addr in usb_addrs:
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
    config_addr = [configs['instruments'][k]['address'] for k in configs['instruments'] if 'address' in k]

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


def open_by_name(name, name_attached=None, filename='config.yaml'):
    """
    Use the system configuration file to open an instrument by name

    Parameters
    ----------
    name : str
        The name of the instrument in the configuration file
    name_attached : str (optional)
        The name attached to the returned object. If not provided the name in the
        configuration file is used
    filename : str
        The YAML configuration filename

    Returns
    -------
    An instrument object

    """
    yaml_config = open(os.path.join(home, filename), 'r')
    configs = yaml.safe_load(yaml_config)

    # confirm name is in the configs
    if name not in configs['instruments']:
        print('Error: {} is not a named instrument in the configuration file')

    cmd_map = os.path.join(configs['csv_directory'],
                           configs['instruments'][name]['csv_folder'],
                           configs['cmd_name'])

    lookup_file = os.path.join(configs['csv_directory'],
                               configs['instruments'][name]['csv_folder'],
                               configs['lookup_name'])

    cmd_list, inst_comm, unconnected = init_instrument(
        cmd_map, addr=configs['instruments'][name]['address'], lookup=lookup_file)

    if bluesky_name is not None:
        name = name_attached

    InstrumentClass = getattr(instruments, configs['instruments'][name]['python_class'])

    return InstrumentClass(cmd_list, inst_comm, name, unconnected)
