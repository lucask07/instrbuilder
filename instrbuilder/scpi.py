# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

'''
The SCPI module includes the SCPI class, functions to convert return values, and builds 
a SCPI object (using the function init_instrument) from a CSV file of commands and lookups.
'''

# standard library imports
import warnings
import time
import sys
import math
import ast
from collections import defaultdict
import functools
# imports that may need installation
import pandas as pd
import colorama
import numpy as np
import serial
import pyvisa as visa
from pyvisa.constants import StatusCode

# local package imports
from instrbuilder.command import Command
from instrbuilder import utils

# -----------------------------------------
# a dictionary of functions that are used to convert return values from getters
convert_return = defaultdict(lambda: str)
convert_return['string'] = str
convert_return['float'] = float
convert_return['double'] = float
convert_return['int'] = int
convert_return['nan'] = str


def arr_str(str_in):
    """ convert string such as '2.3', '5.4', '9.9' to a list of floats """
    return np.asarray(list(map(lambda x: float(x), str_in.split(','))))


def arr_bytes(bytes_in):
    """ convert array of bytes such as b'1,0\r' to a list of floats """
    str_in = bytes_in.decode('utf-8').rstrip()
    return np.asarray(list(map(lambda x: int(x), str_in.split(','))))


def arr_bytes_floats(bytes_in):
    """ convert array of bytes such as b'-3.051776e-004,-3.051776e-004,\r', to a list of floats """
    str_in = bytes_in.decode('utf-8').rstrip()
    return np.asarray(list(map(lambda x: float(x), list(filter(None, str_in.split(','))))))


def str_strip(str_in):
    """ strip whitespace at right of string. Wrap string rstrip method into function """
    return str(str_in.rstrip())


def keysight_error(str_in):
    """ detect for an error return, specific to Keysight. 

    Parameters
    ----------
    str_in : string
        input string to check 

    Returns 
    ----------
    bool
    """
    return str_in[0:2] != '+0'


# add attribute to the getter conversion function so that bluesky
#    (or the generation of a bluesky signal) knows what to do
def returns_array(func):
    func.returns_array = True
    return func

nop = lambda x: x

convert_return['str'] = str_strip
convert_return['str_array_to_numarray'] = returns_array(arr_str)
convert_return['byte_array_to_numarray'] = returns_array(arr_bytes)
convert_return['byte_array_to_numarray_floats'] = returns_array(arr_bytes_floats)
convert_return['keysight_error'] = keysight_error
convert_return['pass'] = nop
convert_return['pass_array'] = returns_array(nop)

# getter conversion function to determine if a single bit is set. Returns True or False
for i in range(8):
    convert_return['bit{}_set'.format(
        i)] = lambda x: bool(functools.partial(utils.get_bit, bit=i)(int(x)))
# getter conversion function to determine if a single bit is cleared. Returns True or False
for i in range(8):
    convert_return['bit{}_cleared'.format(
        i
    )] = lambda x: not bool(functools.partial(utils.get_bit, bit=i)(int(x)))
#### -----------------------------------------
divider_string = '='*80 + '\n'
getter_debug_value = '7'  # when running headless (no instruments attached) all getters return this arbitrary value


class SCPI(object):
    """A SCPI (or SCPI like) instrument with a list of commands. The instrument has methods to get and set info of each command.

    Parameters
    ----------
    cmd_list : Command
        A list of commands. Each command is an object of the class Command
    comm_handle : Communication object
        handle to the (general) hardware interface
        Example is the pyvisa instrument object: inst
        Needed when commands are overriden
        must have a:
            write method (Examples are pySerial write() or pyvisa inst.write())
            and an ask method (Examples are pySerial ask() and pyvisa inst.query())
    name : str, optional
        Name of the instrument 
    unconnected : bool, optional
        For simulation & testing without instruments
        If true a "fake" ask and write command are configured. Ask always returns the same value (getter_debug_value).

    Attributes
    ----------
    unconnected : bool
        if True the instrument is unconnected and returns appropriately 
        configured garbage values just for testing
    vendor_id : str
        id returned by the identification command
    name : str
        name the user assigns 
    comm_handle : object 
        the communication object (could be from pyvisa or pyserial)

    Methods
    ----------
    get(name, configs={}) : 
        get the value for the command of a given name 

    set(name, value=None, configs={}) : 
        set a value for the command of name 

    list_cmds() : 
        print all cmds

    help_all(subsystem_list=None) : 
        list help for all commands (or for commands within a list of subsystems)

    help(name): 
        print help on a command of the provided name 

    log_all_getters(filename=None, suppress_stdout=False):
        write all values that can be read to a file or to stdout

    test_command(name, set_vals=None, get_configs={}, set_configs={}): 
        test a specific command by sending a value and checking the readback of that value 

    test_all(skip_subsystem=['setup', 'status', 'system'],
                 skip_commands=['fast_transfer', 'reset']) : 
        test all commands 

    """

    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='not named',
                 unconnected=False):
        self._cmds = {}
        for cmd in cmd_list:
            self._cmds[cmd.name] = cmd
        self._write = comm_handle.write
        try:
            self._ask = comm_handle.query
        except:
            self._ask = comm_handle.ask  #pyserial
        self.unconnected = unconnected

        # get the vendor ID, which often includes firmware revision and other useful info.
        try:
            vendor_id = self.get('id')
            print('Opened Instrument: {}'.format(vendor_id))
        except Exception as e:
            print(e)
            print(
                'ID command not returned by instrument. Vendor ID set to None')
            vendor_id = None
        self.vendor_id = vendor_id
        self.name = name
        self.comm_handle = comm_handle

    def __dir__(self):
        return self._cmds.keys()

    def __len__(self):
        return len(self._cmds)

    def get(self, name, configs={}):

        if not self._cmds[name].getter:
            print('This command {} is not a getter'.format(name))
            raise NotImplementedError

        if self._cmds[name].getter_override is not None:
            return self._cmds[name].getter_override(**configs)

        cmd_str = self._cmds[name].ascii_str_get
        ret_val = self._ask(cmd_str.format(**configs))

        # if the instrument is not connected, check if the command has a specific return value
        if self.unconnected:
            try:
                ret_val = self._cmds[name]._unconnected_val
            except Exception as inst:
                print(inst)
                pass
        try:
            val = self._cmds[name].getter_type(ret_val)
            # check if a lookup table exists
            if bool(self._cmds[name].lookup):  # bool(dict) --> checks if dictionary is empty
                try:
                    # check if this value matches a key in the lookup table
                    val = list(self._cmds[name].lookup.keys())[list(
                        self._cmds[name].lookup.values()).index(val)]
                except ValueError:
                    print('Warning: {} value of {} not in the lookup table'.
                          format(name, val))
            return val

        except ValueError:
            print('Warning! getter {} returned unexpected type'.format(
                self._cmds[name].name))
            print('  Returned {}; with type = {}; expects = {}'.format(
                ret_val, type(ret_val), self._cmds[name].getter_type))

    def set(self, name, value=None, configs={}):
        """ set a value 
        
        Parameters
        ----------
        name : string
            name of the command (first column in the csv file)
        value : Union[str, int, float, None]
            the value to set  
        configs : dict, optional
            special configurations beyond the 'value'; specified in the csv file

        Returns 
        ----------
        str 
            .. todo:: check this and fix? 

        """
        cmd_str = self._cmds[name].ascii_str

        if value is not None:
            # check if this value is a key in the lookup table
            if value in self._cmds[name].lookup:
                try:
                    value = self._cmds[name].lookup[value]
                except Exception as set_error:
                    pass  # just keep value

            self.check_set_range(value, name)
            cmd_str = cmd_str.format(value=value, **configs)

        # allow for a setter with no value (e.g. '*RST')
        else:  # is the value is None
            cmd_str = cmd_str.format(value='').rstrip()

        # for pytests 
        if self.unconnected:
            self._cmds[name]._unconnected_val = value

        # send the command to the instrument
        return self._write(cmd_str)

    def check_set_range(self, value, name):
        """ check if the value to be set is within range 
        
        Parameters
        ----------
        name : string
            name of the command (first column in the csv file)
        value : Union[str, int, float, None]
            the value to set  

        Returns 
        ----------
        bool  
            True if in range 

        """
        if self._cmds[name].limits is None:
            return True

        if (len(self._cmds[name].limits) == 2) and (type(
                self._cmds[name].limits[0]) is not str):
            # numeric, check if less than or greater than
            if (value >= self._cmds[name].limits[0]) and (
                    value <= self._cmds[name].limits[1]):
                return True
            else:
                # throw out of range warning
                self.out_of_range_warning(value, name)
                return False
        else:
            # check if value is a member
            if value in self._cmds[name].limits:
                return True
            else:
                # throw out of range warning
                self.out_of_range_warning(value, name)
                return False


    def out_of_range_warning(self, value, name):
        """ throw a warning 

        Parameters
        ----------
        value : Union[str, int, float, None]
            the value to set  
        name : string
            name of the command (first column in the csv file)

        Returns 
        ----------
        UserWarning  

        """
        warnings.warn(
            '\n  {} value of {} is out of the range of {}'.format(
                name, value, self._cmds[name].limits), UserWarning)


    def list_cmds(self):
        """ list all commands """
        for key in self._cmds:
            print('{}'.format(self._cmds[key].name))


    def help_all(self, subsystem_list=None):
        """ print help for all commands 

        Parameters
        ----------
        subsystem_list : list, optional
            a list of subsystems to limit the printing to   
        name : string
            name of the command (first column in the csv file)

        """
        if subsystem_list is None:
            # get all subsystems
            subsystems = [self._cmds[d].subsystem for d in self._cmds]
            subsystems = [s if s is not None else 'Unassigned' for s in subsystems]
            # create a list of unique subsystems
            subsystem_set = set(subsystems)
        else:
            subsystem_set = set(subsystem_list)

        for s in subsystem_set:
            print(divider_string)
            print(
                f'Help for Subsytem: {colorama.Fore.RED}{s}{colorama.Style.RESET_ALL}:'
            )
            print('\n')
            for k in self._cmds:
                if self._cmds[k].subsystem == s:
                    self.help(k)
                    print('')

    def help(self, name):
        """ print help for a single command 

        Parameters
        ----------
        name : str
            the name of the command

        """
        if self._cmds[name].subsystem is not None:
            sub_sys = ' in subsystem: {}'.format(self._cmds[name].subsystem)
        else:
            sub_sys = ''

        print(
            f'Help for command {colorama.Fore.GREEN}{self._cmds[name].name}{colorama.Style.RESET_ALL}{sub_sys}:'
        )
        print('    {}'.format(self._cmds[name].doc))
        if self._cmds[name].limits is not None:
            print('    Allowable range is: {}'.format(
                self._cmds[name].limits))
            if len(self._cmds[name].set_config_keys) > 0:
                print(
                    '    The setter needs a configuration dictionary with keys: {}'.
                    format(', '.join(self._cmds[name].set_config_keys)))

        if self._cmds[name].getter:
            print('    Returns: {}'.format(
                self._cmds[name].getter_type.__name__))
            if len(self._cmds[name].set_config_keys) > 0:
                print(
                    '    Getting a value needs a configuration dictionary with keys: {}'.
                    format(', '.join(self._cmds[name].get_config_keys)))

        if len(self._cmds[name].lookup) > 0:
            print('    This command utilizes a lookup table on get and set:')
            print('     ' + str(self._cmds[name].lookup))

    def log_all_getters(self, filename=None, suppress_stdout=False):
        """ save all gettable values to a file and send to stdout
        
        Parameters
        ----------
        filename : str, optional
            name of the file (if None no file is saved)
        suppress_stdout : bool, optional
            if True the getters will not be printed to stdout

        Returns 
        ----------
        dict
            dictionary with the command name as keys and the results as values  

        """
        # .. todo:: read getters that need a configuration input 
        keys = []
        results = []
        for key in self._cmds:
            if self._cmds[key].getter and (self._cmds[key].getter_inputs == 0):
                keys.append(key)
                results.append(self.get(key))

        # print to stdout if not suppressed
        if not suppress_stdout:
            for (key, result) in zip(keys, results):
                print('{} = {}'.format(key, result))

        # write to a file if a file name is provided as input
        if filename is not None:
            with open(filename, 'w') as f:
                print('Time = {}'.format(time.time()), file=f)
                print('Instrument = {}'.format(self.instrument_name), file=f)
                for (key, result) in zip(keys, results):
                    print('{} = {}'.format(key, result), file=f)

        return dict(zip(keys, results))

    def read_comm_err(self):
        """ Read if the instrument has flagged a communciation error 
            The csv command file must have a getter with name comm_error that returns a bool 

        Returns 
        ----------
        bool
            if True a comm error was detected

        """
        try:
            return self.get('comm_error')
        except KeyError as inst:
            print(
                'Error: The command comm_error must be configured to read instrument errors'
            )
            sys.exit()

    def test_command(self, name, set_vals=None, get_configs={},
                     set_configs={}):
        """ Test a command by setting and getting to determine if: 
            1) the instrument reports a communcation error
            2) the return value is of an unexpected type or an error threshold away from what was set
        
            Parameters
            ----------
            name : str
                Name of the command 
            set_vals : list, optional
                A list of values to test by a sequence of set and get.
                If not provided the low and high limits are used 
            get_configs : dict, optional
                A dictionary of configs to send the get command
            set_configs : dict, optional
                A dictionary of configs to send the set command

            Returns
            -------
            bool
                True if the command is successful, False otherwise.

            Example
            -------
            dmm.test_command('curr_range', set_configs = {'ac_dc':'DC'}, get_configs = {'ac_dc':'DC'})

        """

        comm_error = False
        allowed_err = 0.02  # .. todo:: determine error magnitude that is allowed for automated checking

        if (len(self._cmds[name].get_config_keys) != len(get_configs)) or (len(
                self._cmds[name].set_config_keys) != len(set_configs)):
            print('Skipping test of: {}'.format(name))
            print(
                '  Automated test of getters or setters that require a configuration input is not yet implemented'
            )
            print('An input configuration dictionary is required')
            return 'NotTested'

        # if getter and setter
        if (self._cmds[name].getter and self._cmds[name].setter):

            ret = self.get(name, configs=get_configs)
            comm_error |= self.read_comm_err()
            if set_vals is None:
                try:
                    set_vals = [
                        self._cmds[name].limits[0], self._cmds[name].limits[1]
                    ]
                except :
                    print(
                        'Skipping test of setter {} since limits are missing'.
                        format(name))
                    return 'NotTested'

            for set_val in set_vals:
                self.set(name, set_val, configs=set_configs)
                comm_error |= self.read_comm_err()
                ret = self.get(name, configs=get_configs)
                # if present remove lookup table modification
                try:
                    ret = self._cmds[name].lookup[ret]
                except:
                    pass

                comm_error |= self.read_comm_err()
                if self._cmds[name].getter_type == float:
                    try:
                        deviates = np.abs(
                            (ret - set_val) / set_val) > allowed_err
                    except ZeroDivisionError:
                        deviates = (ret != set_val)
                else:
                    deviates = (ret != set_val)

                    if deviates:
                        comm_error = True
                        if self._cmds[name].getter_type == float:
                            print(
                                'Get vs. set difference greater than {} %% for command {}'.
                                format(allowed_err * 100, name))
                        else:
                            print(
                                'Get vs. set difference for command {}'.format(
                                    name))
                        print('Set {}; got {}'.format(set_val, ret))
                        print(divider_string)

        # if setter only
        elif self._cmds[name].setter:
            if (self._cmds[name].limits) is None:
                set_val = None
                self.set(name, set_val, configs=set_configs)
                comm_error |= self.read_comm_err()

            elif (len(self._cmds[name].limits) > 2):
                set_vals = [
                    self._cmds[name].limits[0], self._cmds[name].limits[-1]
                ]
                for set_val in set_vals:
                    self.set(name, set_val, configs=set_configs)
                    comm_error |= self.read_comm_err()
            else:
                print('Skipping test of setter {}'.format(name))
                return 'NotTested'

        # if getter only
        elif self._cmds[name].getter:
            ret = self.get(name, configs=get_configs)
            comm_error |= self.read_comm_err()

        else:
            print('Command is not a setter nor a getter, cannot test!')

        return not comm_error

    def test_all(self,
                 skip_subsystem=['setup', 'status', 'system'],
                 skip_commands=['fast_transfer', 'reset']):
        """ Test all commands by setting and getting to determine if: 
            1) the instrument reports a communcation error
            2) the return value is of an unexpected type or an error threshold away from what was set
        
            Parameters
            ----------

            skip_subsystem : list (of strings), default = ['setup', 'status']
                subsystems to skip, an example might be commands in the status subsystem
                that reset the instrument 
            skip_commands : list (of strings), default = ['fast_transfer', 'reset']
                Commands to skip

            Returns
            -------
            dict
                Keys are each commands tested, value is True (command succeeded) or False (command errored)

        """
        all_tests = {}
        for key in self._cmds:
            if (self._cmds[key].subsystem in skip_subsystem) or (
                    key in skip_commands):
                pass
            else:
                print('Testing {}'.format(key))
                status = self.test_command(key)
                all_tests[key] = status
                print('Result for {} = {}'.format(key, status))

        #### ---- Print and return results -----
        print('\n')
        print(divider_string)
        print('Command Test Results:')
        import pprint
        pprint.pprint(all_tests)
        print('Returns True if command is successful')
        return all_tests


class PyVisaUSB(object):
    """A USBPyVISA instrument (connected via a USB cable)

    Parameters
    ----------
    address: str 
        the address of the device

    Attributes
    ----------
    comm : visa communciation object 
    
    """

    def __init__(self, address):
        try:
            self.comm = self.open_visa(address)
        except Exception as inst:
            print(inst)
            print('Device Opening failed')


    def open_visa(self, addr):
        """ open a VISA object 
        Parameters
        ----------
        addr : str
            the address of the device

        Returns
        ----------
        PyVISA object

        .. todo::
           * determine if error flag
           * enable or disable of lookup table   
        
        """

        mgr = visa.ResourceManager()
        resources = mgr.list_resources()
        if addr in resources:
            # open device  .. todo:: check return value
            obj = mgr.open_resource(addr)
        elif addr not in resources:
            print(
                'Trying to open the device even though it was not found by the resource manager'
            )
            obj = mgr.open_resource(addr)
        else:
            print(
                'This address {} was not recognized'.format(addr),
                file=sys.stderr)
            print('Returning an empty handle', file=sys.stderr)
            obj = None
        return obj

    def ask(self, cmd):
        """ Send a query to the instrument 

        Parameters
        ----------
        cmd : str
            the ASCII string sent to the device

        Returns
        ----------
        str
            ASCII string returned by the device 

        """
        res = self.comm.query(cmd)
        return res

    def write(self, cmd):
        """ Write a command to the instrument 

        Parameters
        ----------
        cmd : str
            the ASCII string sent to the device

        Returns
        ----------
        bool
            if True transaction was successful  
        str
            returned value   .. todo:: check this  
        
        """
        ret = self.comm.write(cmd)
        return ret[1] == StatusCode.success, ret

    def close(self):
        pass


class Serial(object):
    """A PySerial instrument (connected via a serial cable, i.e. RS232)

    Parameters
    ----------
    ser_port : str 
        the address of the device (example on a MAC is '/dev/tty.USA19H141113P1.1')

    baudrate : int, optional
        the serial channel baudrate to configure

    parity : str, optional
        options given by serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD

    bytesize : int, optional
        options given by serial.EIGHTBITS, serial.FIVEBITS, serial.SEVENBITS

    Attributes
    ----------
    ser : the serial communciation object 

    terminator : the termination character to send 

    """
    def __init__(self, ser_port, **kwargs):
        self.ser = serial.Serial(
            port=ser_port,
            baudrate=kwargs.get('baudrate', 9600),
            parity=kwargs.get('parity', serial.PARITY_NONE),
            bytesize=kwargs.get('bytesize', serial.EIGHTBITS))
        self.terminator = kwargs.get('terminator', ' \n')
        self.eol = kwargs.get('eol', b'\r')
        self.open()

        # some instruments need an initialization write,
        #   i.e. turn on remote interface mode
        init_write = kwargs.get('init_write')
        if init_write is not None:
            self.write(init_write)

    def open(self):
        self.ser.close()
        self.ser.open()

        cnt = 0
        while not self.ser.isOpen():
            time.sleep(0.1)
            cnt = cnt + 1
            if cnt > 25:
                print('Failed to open Serial interface at address: {}'.format(
                    self.ser_port))

    def ask(self, cmd):
        self.write(cmd)
        res = self._readline()
        return res

    def write(self, cmd):
        cmd = cmd + self.terminator
        self.ser.write(cmd.encode('utf-8'))
        return (True,
                'no-details')  # pyserial does not return a success upon write

    def close(self):
        self.ser.close()

    # https://stackoverflow.com/questions/16470903/pyserial-2-6-specify-end-of-line-in-readline
    def _readline(self):
        #eol = b'\r'
        leneol = len(self.eol)
        line = bytearray()
        while True:
            c = self.ser.read(1)
            if c:
                line += c
                if line[-leneol:] == self.eol:
                    break
            else:
                break
        return bytes(line)


def init_instrument(cmd_map, addr, lookup=None, **kwargs):
    """
    initialize an instrument with its address and CSV file of commands 

    Parameters
    ----------
    cmd_map : str
        path to the CSV file of instrument commands 
    addr : dict 
        key is one of pyserial, pyvisa; value is the address of the instrument
    lookup : str, optional
        filename of the CSV file of lookup table

    Returns
    ----------
    list 
        list of commands that will be used for building the instrument
    object
        communication handle
    bool 
        True if instrument is not connected  
    
    """

    # Read CSV file of commands using Pandas
    df = pd.read_csv(cmd_map)
    # strip white space and end-of-line from column headers
    df = df.rename(columns=lambda x: x.strip())
    # strip white space and end-of-line from string inputs
    df['setter_type'] = df['setter_type'].str.strip()
    df['getter_type'] = df['getter_type'].str.strip()

    # Read CSV file of lookups
    if lookup:
        df_look = pd.read_csv(lookup)
        # strip white space and end-of-line from column headers
        df_look = df_look.rename(columns=lambda x: x.strip())
        # drop empty rows (for example, at the end)
        df_look = df_look.dropna(how='all')

        # make a dictionary for each command
        cmd_lookups = {}
        for index, row in df_look.iterrows():
            if index == 0:
                try:
                    if math.isnan(row['command']):
                        raise Exception(
                            'The first element of the lookup table is empty')
                except Exception as inst:
                    pass
            try:
                if not math.isnan(row['command']):
                    current_cmd = current_cmd  # shouldn't get here
            except Exception as inst:
                current_cmd = row['command']

            try:
                dict_key = float(row['name'])
            except ValueError:
                dict_key = str(row['name'])

            if current_cmd in cmd_lookups.keys():
                cmd_lookups[current_cmd][dict_key] = row['value']
            else:
                # initialize the dictionary
                cmd_lookups[current_cmd] = {}
                cmd_lookups[current_cmd][dict_key] = row['value']

    cmd_list = []
    for index, row in df.iterrows():
        # convert getter, setter to Boolean True or False
        for gs in ['getter', 'setter']:
            if row[gs] in ['True', 'T', 'TRUE', 'true', True]:
                tmp = True
            elif row[gs] in ['False', 'F', 'FALSE', 'false', False]:
                tmp = False
            else:
                tmp = False
            row[gs] = tmp  # converts to Boolean

        if row['setter_range'] is not None:
            try:
                row['setter_range'] = ast.literal_eval(row['setter_range'])
            except ValueError:
                if not math.isnan(row["setter_range"]):
                    print(
                        f'Warning setter_range of {colorama.Fore.GREEN}{row["setter_range"]}{colorama.Style.RESET_ALL} for command {colorama.Fore.BLUE}{row["name"]}{colorama.Style.RESET_ALL} not of proper form'
                    )
                row['setter_range'] = None

        # pandas read default value is nan. Convert to None or 0 depending upon column
        def modify_default(row_el, default_value):
            try:
                row_el = default_value if math.isnan(row_el) else row_el
            except TypeError:
                row_el = row_el
            return row_el

        row['setter_inputs'] = modify_default(row['setter_inputs'], 1)
        row['getter_inputs'] = modify_default(row['getter_inputs'], 0)
        row['ascii_str_get'] = modify_default(row['ascii_str_get'], None)
        row['subsystem'] = modify_default(row['subsystem'], None)

        if False:
            print('---')
            print(row['name'])
            print(cmd_lookups.keys())
            print('---')

        if row['name'] in cmd_lookups.keys():
            lookup_dict = cmd_lookups[row['name']]
        else:
            lookup_dict = {}

        cmd = Command(
            name=row['name'],
            ascii_str=row['ascii_str'],
            ascii_str_get=row['ascii_str_get'],
            getter=row['getter'],
            getter_type=convert_return[row['getter_type']],
            setter=row['setter'],
            setter_type=convert_return[row['setter_type']],
            limits=row['setter_range'],
            doc=row['doc'],
            subsystem=row['subsystem'],
            getter_inputs=row['getter_inputs'],
            setter_inputs=row['setter_inputs'],
            lookup=lookup_dict,
            is_config=row['is_config'])

        cmd_list.append(cmd)

    # check to ensure the dictionary only has 0 or 1 entry
    if len(addr) > 1:
        sys.exit('Multiple keys: {}'.format(list(addr.keys())))
    # pySerial:Serial
    if 'pyserial' in addr:
        try:
            inst = Serial(addr['pyserial'], **kwargs)
            inst_comm = inst
            inst_comm.ser.flush()
            unconnected = False
        except Exception as inst:
            print(inst)
            unconnected = True
            print('PySerial address not found {}'.format(addr['pyserial']))
            print('Possible serial addresses:')
            import glob
            import platform
            if platform.system() == 'Darwin':
                print('On your MAC at /dev/tty.USA*')
                print(glob.glob("/dev/tty.USA*"))
            elif platform.system() == 'Linux':
                print('On your Linux Box at /dev/tty.USA* ??')
                print(glob.glob("/dev/tty.USA*"))
            elif platform.system() == 'Windows':
                print('On your Windows Machine I do not know how to check for available COM ports')
                #print(glob.glob("/dev/tty.USA*"))
    # pyvisa:PyVisaUSB
    elif 'pyvisa' in addr:
        try:
            inst = PyVisaUSB(addr['pyvisa'])
            inst_comm = inst.comm
            unconnected = False
        except Exception as e:
            print(e)
            unconnected = True
            print('PyVISA address {} not found'.format(addr['pyvisa']))
    # unattached instrument
    else:
        unconnected = True
    if unconnected: #Targeting a PyVISA like instrument
        # allow for debugging without instruments attached:
        #   print command to stdout, always return getter_debug_value
        print(divider_string, end='')
        print('Running in debug mode without instrument attached')
        print('All commands sent to the instrument will be printed to stdout.')
        print(
            'Unless specified by cmd attribute _unconnected_val' +  
            ' \ngetters will always return {} (getter_debug_value)'.
            format(getter_debug_value))
        print(divider_string)

        class Comm():
            pass

        inst_comm = Comm()

        def ask(str_input):
            print(str_input)
            return getter_debug_value

        def write(str_input):
            print(str_input)

        inst_comm.write = write
        inst_comm.query = ask

    return cmd_list, inst_comm, unconnected
