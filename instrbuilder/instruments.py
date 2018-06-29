# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports

import numpy as np
import sys
import time

# local package imports
sys.path.append(
    '/Users/koer2434/instrbuilder/')  # this instrbuilder: the SCPI library
from scpi import SCPI


# TODO: Extra capabilites should be moved somewhere else
def filewriter(data, filename, filetype='png'):
    ''' Write a list or np.array of unsigned bytes to a file 

    Parameters
    ----------
    data : list or np.array
        data to save to file
    write : str 
        filename without extension (if no directory is provided will save to cwd)
    filetype : str 
        type of file: options implemented are 'png' and 'npy'
    '''
    print('Saving file: {}'.format(filename + '.' + filetype))
    if filetype == 'png':
        with open(filename + '.' + filetype, 'wb') as out_f:
            out_f.write(bytearray(data))
    elif filetype == 'npy':
        np.save(filename + '.' + filetype, data)


class AgilentFunctionGen(SCPI):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='fg',
                 unconnected=False):
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)


class KeysightFunctionGen(SCPI):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='fg',
                 unconnected=False):
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)


class KeysightOscilloscope(SCPI):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='osc',
                 unconnected=False):
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)
        # Override of "single line" SCPI functions
        self._cmds['display_data'].getter_override = self.display_data

    def display_data(self):

        t = self.comm_handle.query_binary_values(
            ':DISP:DATA? PNG, COL', datatype='B', header_fmt='ieee')
        self.comm_handle.query_delay = 0.0
        return np.array(t, dtype='B')

    def save_display_data(self, filename, filetype='png'):
        """ get the display_data from the display and save to a file """
        filewriter(self.display_data(), filename, filetype)

class KeysightMSOX3000(KeysightOscilloscope):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='osc',
                 unconnected=False):
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)


class SRSLockIn(SCPI):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='lia',
                 unconnected=False):
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)

        if unconnected:
            # TODO: Remove this hack.
            #       How to ensure the commands unconnected value works with the getter conversion function?
            self._cmds['ch1_disp']._unconnected_val = b'1,0\r'

    def test_composite_get(self):
        f = self.get('freq')
        self.set(f*1.2, 'freq')
        return float(self.get('freq'))

    def test_composite_set(self, value):
        self.set(value[0], 'freq')
        self.set(value[1], 'tau')
        return self.set(value[2], 'sensitivity')


class KeysightMultimeter(SCPI):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='dmm',
                 unconnected=False):
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)

        # Override of "single line" SCPI functions
        self._cmds['hardcopy'].getter_override = self.hardcopy
        self._cmds['burst_volt'].getter_override = self.burst_volt 

    # Override getter functions -- these overrides should be compatible with Bluesky
    #                              (in other words return a signal value, which can be an np.array)
    def hardcopy(self):
        """ Transfers a hard-copy (image) of the screen to the host as a  """

        self.comm_handle.query_delay = 4

        img_data = self.comm_handle.query_binary_values(
            'HCOP:SDUM:DATA?', datatype='B', header_fmt='ieee')
        self.comm_handle.query_delay = 0.0
        return np.array(img_data, dtype='B')  # unsigned byte
        # see: https://docs.scipy.org/doc/numpy-1.13.0/reference/arrays.dtypes.html

    # Composite functions (examples)
    def save_hardcopy(self, filename, filetype='png'):
        """ get the hardcopy data from the display and save to a file """
        filewriter(self.hardcopy(), filename, filetype)

    def burst_volt(self, reads_per_trigger=1, aperture=1e-3,
                    trig_source='BUS', trig_count=1, trig_slope = 'POS',
                    volt_range=10, trig_delay=None):
        """
        measure a burst of triggered voltage readings
        """
        self.set(aperture, 'volt_aperture')
        self.set(trig_source, 'trig_source')  # BUS = remote interface (host); EXT = external signal 
        if trig_source == 'EXT':
            self.set(trig_slope, 'trig_slope')
        self.set(trig_count, 'trig_count')
        self.set(reads_per_trigger, 'sample_count')
        self.set(0, 'volt_range_auto', configs={'ac_dc': 'DC'}) # turn off auto-range
        self.set(volt_range, 'volt_range', configs={'ac_dc': 'DC'}) # set range
        if trig_delay is not None:
            self.set(trig_delay, 'trig_delay')
        self.set(None, 'initialize')
        if trig_source == 'BUS':
            print('Sending (bus) trigger command')
            self.set(None, 'trig')
        print('Expecting {} readings'.format(trig_count * reads_per_trigger))

        x = self.get('fetch')
        return x

    def burst_volt_setup(self, reads_per_trigger=1, aperture=1e-3,
                         trig_source='EXT', trig_count=1, trig_slope='POS',
                         volt_range=10, trig_delay=None):
        """
        measure a burst of triggered voltage readings that are saved to the instruments flash
        and then downloaded at the end
        """
        self.set(aperture, 'volt_aperture')
        self.set(trig_source, 'trig_source')  # BUS = remote interface (host); EXT = external signal
        if trig_source == 'EXT':
            self.set(trig_slope, 'trig_slope')
        self.set(trig_count, 'trig_count')
        self.set(reads_per_trigger, 'sample_count')
        self.set(0, 'volt_range_auto', configs={'ac_dc': 'DC'}) # turn off auto-range
        self.set(volt_range, 'volt_range', configs={'ac_dc': 'DC'}) # set range
        if trig_delay is not None:
            self.set(trig_delay, 'trig_delay')

    def burst_volt_save(self, reads_per_trigger=1,
                        trig_source='EXT', trig_count=1, repeats=4,
                        filename='test_{}'):
        # MMEMory:STORe:DATA RDG_STORE, <file> pg 306,
        # initialize clears the memory
        for i in range(repeats):
            self.set(None, 'initialize')
            if trig_source == 'BUS':
                print('Sending (bus) trigger command')
                self.set(None, 'trig')
            print('Expecting {} readings'.format(trig_count * reads_per_trigger))

            while self.get('operation_complete') == 0:
                time.sleep(0.005)
            self.set(filename.format(i), 'store_data')

        # Timing of this function showed that it is not a method to optimize speed
        # 200 measurements triggered at 780 Hz (256 ms of capture time) required 613 ms with the file-saving

    def burst_volt_upload(self, repeats=4):
        # read and unpack the binary data (8 byte IEEE-754 format)

        # cannot use the standard SCPI get since we need to read raw binary data and apply a
        #    different decoding
        # x = self.get('upload_data', configs={'filename': filename.format(0)})

        data_array = np.array([])
        header_offset_bytes = 5
        bytes_per_val = 8
        for file_idx in range(repeats):
            self.comm_handle.write('MMEM:UPL? "test_{}.dat"'.format(file_idx))
            binary_data = self.comm_handle.read_raw()
            from struct import unpack
            num_values = int((len(binary_data)-header_offset_bytes-1)/bytes_per_val)
            unpacked_data = unpack("<{}d".format(num_values), binary_data[header_offset_bytes:-1])
            data_array = np.append(data_array, unpacked_data)

        return data_array
