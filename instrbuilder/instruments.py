# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports
import numpy as np
import sys
import time

# local package imports
from instrbuilder.scpi import SCPI


class RigolPowerSupply(SCPI):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='pwr',
                 unconnected=False,
                 channels=(1, 2, 3)):
        self._channels = channels
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)


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

class KeysightSMU(SCPI):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='smu',
                 unconnected=False):
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)

class RigolOscilloscope(SCPI):
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
            ':DISP:DATA? PNG, ON', datatype='B', header_fmt='ieee')
        return np.array(t, dtype='B')

    def save_display_data(self, filename, filetype='png'):
        """ get the display_data from the display and save to a file """
        filewriter(self.display_data(), filename, filetype)

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
            self._cmds['ch1_disp']._unconnected_val = b'1,0\r'


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
        self._cmds['burst_volt_timer'].getter_override = self.burst_volt_timer

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

    # ------ Composite functions (examples) ------
    #
    # --------------------------------------------
    def save_hardcopy(self, filename, filetype='png'):
        """ get the hardcopy data from the display and save to a file """
        filewriter(self.hardcopy(), filename, filetype)

    def burst_volt(self, reads_per_trigger=1, aperture=1e-3,
                    trig_source='BUS', trig_count=1, trig_slope = 'POS',
                    volt_range=None, trig_delay=None):
        """
        Composite function to measure a burst of voltages
        measure a burst of triggered voltage readings
        """
        self.set('volt_aperture', aperture)
        self.set('trig_source', trig_source)  # BUS = remote interface (host); EXT = external signal
        if trig_source == 'EXT':
            self.set('trig_slope', trig_slope)
        self.set('trig_count', trig_count)
        self.set('sample_count', reads_per_trigger)
        if volt_range is not None:
            self.set('volt_range_auto', 0, configs={'ac_dc': 'DC'}) # turn off auto-range
            self.set('volt_range', volt_range, configs={'ac_dc': 'DC'}) # set range
        if trig_delay is not None:
            self.set('trig_delay', trig_delay)
        self.set('initialize')
        if trig_source == 'BUS':
            print('Sending (bus) trigger command')
            self.set('trig')
        print('Expecting {} readings'.format(trig_count * reads_per_trigger))

        x = self.get('fetch')
        return x

    def burst_volt_timer(self, reads_per_trigger=256, aperture=20e-6,
                         trig_source='EXT', trig_count=1, trig_slope='POS',
                         volt_range=None, trig_delay=0, sample_timer=0.4096e-3,
                         repeats=16):
        """
        measure a burst of triggered voltage readings
        maximum rate of external trigger is 5 kHz
        """
        self.set('volt_aperture', aperture)
        self.set('trig_source', trig_source)  # BUS = remote interface (host); EXT = external signal
        if trig_source == 'EXT':
            self.set('trig_slope', trig_slope)
        self.set('volt_autozero_dc', 0)
        self.set('trig_count', trig_count)
        self.set('sample_count', reads_per_trigger)
        if volt_range is not None:
            self.set('volt_range_auto', 0, configs={'ac_dc': 'DC'})  # turn off auto-range
            self.set('volt_range', volt_range, configs={'ac_dc': 'DC'})  # set range

        self.set('sample_source', 'TIM')
        self.set('sample_timer', sample_timer)
        if trig_delay is not None:
            self.set('trig_delay', trig_delay)

        total_arr = np.array([])
        for i in range(repeats):
            self.set('initialize')
            if trig_source == 'BUS':
                print('Sending (bus) trigger command')
                self.set('trig')
            # print('Expecting {} readings'.format(trig_count * reads_per_trigger))

            x = self.get('fetch')
            total_arr = np.append(total_arr, x)
        return total_arr

    def burst_volt_setup(self, reads_per_trigger=1, aperture=1e-3,
                         trig_source='EXT', trig_count=1, trig_slope='POS',
                         volt_range=10, trig_delay=None):
        """
        measure a burst of triggered voltage readings that are saved to the instruments flash
        and then downloaded at the end
        """
        self.set('volt_aperture', aperture)
        self.set('trig_source', trig_source)  # BUS = remote interface (host); EXT = external signal
        if trig_source == 'EXT':
            self.set('trig_slope', trig_slope)
        self.set('trig_count', trig_count)
        self.set('sample_count', reads_per_trigger)
        self.set('volt_range_auto', 0, configs={'ac_dc': 'DC'}) # turn off auto-range
        self.set('volt_range', volt_range, configs={'ac_dc': 'DC'}) # set range
        if trig_delay is not None:
            self.set('trig_delay', trig_delay)

    def burst_volt_save(self, reads_per_trigger=1,
                        trig_source='EXT', trig_count=1, repeats=4,
                        filename='test_{}'):
        # MMEMory:STORe:DATA RDG_STORE, <file> pg 306,
        # initialize clears the memory
        for i in range(repeats):
            self.set('initialize')
            if trig_source == 'BUS':
                print('Sending (bus) trigger command')
                self.set('trig')

            while self.get('operation_complete') == 0:
                time.sleep(0.005)
            self.set('store_data', filename.format(i), )

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


class KeysightNetworkAnalyzer(SCPI):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='pna',
                 unconnected=True,
                 channels=(1, 2, 3, 4)):
        self._channels = channels
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)

        self._cmds['snp_port_data'].getter_override = self.snp_port_data

    def snp_port_data(self):
        # data format lookups
        datatypes = {32: 'f', 64: 'd'}
        dtypes = {32: np.float32, 64: np.float64}

        # 1 frequency channel + N^2 complex vectors
        n_vec = 1 + 2 * len(self._channels) ** 2;

        # retrieve format setting
        fd = int(self.get("form_data").split(",")[-1])

        # trigger reading
        self.set("immediate")

        # wait for operation complete
        while (self.get("opc") & 0x1) == 0:
            pass
   
        # retrieve binary data
        raw = self.comm_handle.query_binary_values(
            'CALCulate:DATA:SNP:PORTs? "{}"'.format(
                ",".join([str(chan) for chan in self._channels])),
            datatype=datatypes[fd])

        # flat array of data format
        flat = np.array(raw, dtype=dtypes[fd])

        # reshape into components
        return flat.reshape((n_vec, int(flat.size / n_vec)))


class TestInstrument(SCPI):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='tester',
                 unconnected=True):
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)

    

try:
    # for Aardvark SPI control
    from .command import Register
    from .ic import IC
    from .ic import AA  # aardvark adapter

    def create_ada2200():

        # ADA2200 register map
        reg_map = {'serial_interface': 			0x0000,  # MSBs
                   'chip_type': 				0x0006,
                   'filter0':					0x0011,
                   'analog_pin':				0x0028,
                   'sync_control':				0x0029,
                   'demod_control':				0x002A,
                   'digital_pin':               0x002C,
                   'clock_config':				0x002B}
        # add other filter configuration registers
        for i in range(1, 23):
            reg_map['filter{}'.format(i)] = 0x0011 + i

        regs = []
        for r in reg_map:
            regs.append(Register(name=r, address=reg_map[r],
                                 read_write='R/W', is_config=True))

        aardvark = AA()  # communication adapter
        ada2200_scpi = IC(regs, aardvark,
                          interface='SPI', name='ADA2200')
        return ada2200_scpi

except: 
    def create_ada2200():
        print('ADA2200 will not work. Aardvark not imported correctly!')
        pass
    print("Error: ", sys.exc_info()[0])
    print('IC (integrated circuit imports failed)')
    print('The aardvark.so or dll must be in the cwd or an importable path')
    print('Continuing anyways, since many may not use this portion...')

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
