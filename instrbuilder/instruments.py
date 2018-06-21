# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports

import numpy as np
import sys

# local package imports
sys.path.append(
    '/Users/koer2434/instrbuilder/')  # this instrbuilder: the SCPI library
from scpi import SCPI


## Extra capabilites should be moved somewhere else
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
                 name='not named',
                 unconnected=False):
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)


class SRSLockIn(SCPI):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='not named',
                 unconnected=False):
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)

        if unconnected:
            # TODO: Remove this hack.
            #       How to ensure the commands unconnected value works with the getter conversion function?
            self._cmds['ch1_disp']._unconnected_val = b'1,0\r'


class KeysightMultimeter(SCPI):
    def __init__(self,
                 cmd_list,
                 comm_handle,
                 name='not named',
                 unconnected=False):
        super().__init__(
            cmd_list, comm_handle, name=name, unconnected=unconnected)

        # Override of "single line" SCPI functions
        self._cmds['hardcopy'].getter_override = self.hardcopy

    ## Override getter functions -- these overrides should be compatible with Bluesky
    ##                              (in other words return a signal value that can be an np.array)
    def hardcopy(self, configs={}):
        ''' Transfers a hard-copy (image) of the screen to the host as a  '''

        self.comm_handle.query_delay = 4

        img_data = self.comm_handle.query_binary_values(
            'HCOP:SDUM:DATA?', datatype='B', header_fmt='ieee')
        self.comm_handle.query_delay = 0.0
        return np.array(img_data, dtype='B')  #unsigned byte
        #   [see: https://docs.scipy.org/doc/numpy-1.13.0/reference/arrays.dtypes.html]

    ## Composite functions (examples)
    def save_hardcopy(self, filename, filetype='png'):
        ''' get the hardcopy data from the display and save to a file '''
        filewriter(self.hardcopy(), filename, filetype)

    ''' TODO: test 
    def triggered_burst(self, readings, delay = 0, sample_count = 1):
        
        self.set('EXT', 'trig_source')
        self.set(readings, 'trig_count')
        self.set(sample_count, 'sample_count')
        self.set(0, 'volt_range_auto', configs = {'ac_dc':'DC'})
        self.set(None, 'initialize')
        self.set(None, 'trigger')

        x = self.get('fetch') # converted to a np.array using: list(map(float, x.split(','))) # a list of values
        return x 

    '''

    def burst_volt(self, reads, aperture=1e-3):
        ''' measure a burst of voltage readings, triggered over the remote interface
        '''
        self.set(aperture, 'volt_aperture')
        self.set('BUS', 'trig_source')  # BUS = remote interface trigger
        self.set(1, 'trig_count')
        self.set(reads, 'sample_count')
        self.set(0, 'volt_range_auto', configs={'ac_dc': 'DC'})
        self.set(None, 'initialize')
        self.set(None, 'trigger')

        x = self.get(
            'fetch'
        )  # converted to a np.array using: list(map(float, x.split(','))) # a list of values
        return x
