# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports
import warnings
import time
import sys
import math
import ast
from collections import defaultdict
import functools

# required package from TotalPhase
from .aardvark_py import *

# local package imports
from .command import Register
from . import utils


class IC(object):
    """An integrated circuit with a list of registers and
    an communication object to read and write to those registers.

    .. todo::
        *

    Parameters
    ----------
    reg_list : Register
        A list of registers. Each register is an object of the class Register
    comm_handle : Communication object
        handle to the (general) hardware interface
        Example is the aardvark
            write method
            ask method
    name : str, optional
        Name of the IC

    # Register
    self.name = name
    self.address = address
    self.read_write = read_write
    self.is_config = is_config

    """
    def __init__(self,
                 reg_list,
                 comm_handle,
                 interface,
                 name='not_named',
                 slave_address=None,
                 unconnected=False):
        self._cmds = {}
        for reg in reg_list:
            self._cmds[reg.name] = reg  # maintain cmds for compatibility with upper-layers (ophyd)
        self._write = comm_handle.write
        self._ask = comm_handle.ask
        self.comm_handle = comm_handle
        self.interface = interface  # SPI or I2C
        self.name = name
        self.unconnected = unconnected  # not yet supported
        self.slave_address = slave_address

    def get(self, name, configs={}):

        # check if R or RW
        if self._cmds[name].read_write not in ['R', 'R/W']:
            print('This register {} is not readable'.format(name))
            raise NotImplementedError

        return self._ask(self.interface, addr_instruction=self._cmds[name].address,
                         slave_address=self.slave_address)

    def set(self, name, value, configs={}):

        if self._cmds[name].read_write in ['W', 'R/W']:
            return self._write(self.interface, addr_instruction=self._cmds[name].address,
                              slave_address=self.slave_address, data=value)
        elif self._cmds[name].read_write in ['R']:
            print('register {} is read-only'.format(name))
            return -1
        else:
            print('register {} does not have R/W configured'.format(name))
            return -1

## Portions of the code for the AA class 
#  below are vendored from the TotalPhase Aardvark API:

#==========================================================================
# Copyright (c) 2002-2008 Total Phase, Inc.
# All rights reserved.
# www.totalphase.com
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# - Neither the name of Total Phase, Inc. nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE. 
#==========================================================================


class AA(object):
    """An Aardvark I2C adapter

        Parameters
        ----------
        comm : Aardvark object
            handle to the opened instrument 

        Methods
        ----------
        open() : 

        configure_i2c(bit_rate) : 

        configure_spi(SPI_BITRATE=1000) : 

        write_i2c(slave_addr, sub_addr, value) : 

        read_i2c(slave_addr, sub_addr, num_bytes_to_read=1) : 

        read_spi(instruction) : 

        ask(interface, addr_instruction, slave_address=None,
             num_bytes_to_read=1) : 
            more generic ask command that propagates to upper-layers

        write(interface, addr_instruction, data, slave_address=None) :
            more generic write command that propagates to upper-layers

    """

    def __init__(self, bitrate = 1000):
        self.comm = self.open()  # handle to the opened Aardvark
        self._bitrate = bitrate
        self.configure_i2c(self._bitrate)
        self.configure_spi()

    def open(self):
        """ open the aardvark handle

        """
        (num, ports, unique_ids) = aa_find_devices_ext(16, 16)
        if num > 1:
            print("More than 1 device, which we don't know what to do with")
        if num > 0:
            print("%d device(s) found:" % num)

            # Print the information on each device
            for i in range(num):
                port = ports[i]
                unique_id = unique_ids[i]

                # Determine if the device is in-use
                inuse = "(avail)"
                if port & AA_PORT_NOT_FREE:
                    inuse = "(in-use)"
                    port = port & ~AA_PORT_NOT_FREE
                    raise Exception('Port is already open')
                # Display device port number, in-use status, and serial number
                print("    port = %d   %s  (%04d-%06d)" %
                      (port, inuse, unique_id // 1000000, unique_id % 1000000))
        else:
            print("No devices found.")

        return aa_open(ports[0])

    def configure_i2c(self, bit_rate):
        """ configure the I2C system """

        # Ensure that the I2C subsystem is enabled
        aa_configure(self.comm, AA_CONFIG_SPI_I2C)

        # Enable the I2C bus pullup resistors (2.2k resistors).
        # This command is only effective on v2.0 hardware or greater.
        # The pullup resistors on the v1.02 hardware are enabled by default.
        aa_i2c_pullup(self.comm, AA_I2C_PULLUP_BOTH)

        # Enable the Aardvark adapter's power supply.
        # This command is only effective on v2.0 hardware or greater.
        # The power pins on the v1.02 hardware are not enabled by default.
        aa_target_power(self.comm, AA_TARGET_POWER_BOTH)

        # Set the bitrate
        bitrate = aa_i2c_bitrate(self.comm, bit_rate)
        print('I2C bitrate set to {} kHz'.format(bitrate))

    def configure_spi(self, SPI_BITRATE=1000):
        # Ensure that the SPI subsystem is enabled
        aa_configure(self.comm, AA_CONFIG_SPI_I2C)

        # Enable the Aardvark adapter's power supply.
        # This command is only effective on v2.0 hardware or greater.
        # The power pins on the v1.02 hardware are not enabled by default.
        aa_target_power(self.comm, AA_TARGET_POWER_BOTH)

        # Setup the clock phase
        mode = 0
        
        # print("  mode 0 : pol = 0, phase = 0")
        # print("  mode 1 : pol = 0, phase = 1")
        # print("  mode 2 : pol = 1, phase = 0")
        # print("  mode 3 : pol = 1, phase = 1")
        aa_spi_configure(self.comm, mode >> 1, mode & 1, AA_SPI_BITORDER_MSB)

        # Set the bitrate
        bitrate = aa_spi_bitrate(self.comm, SPI_BITRATE)
        print("SPI Bitrate set to {} kHz".format(bitrate))

    def write_i2c(self, slave_addr, sub_addr, value):

        # Write the data to the bus
        data = array('B', [sub_addr, value])
        count = aa_i2c_write(self.comm, slave_addr, AA_I2C_NO_FLAGS, data)

        if count < 0:
            print("error: %s" % aa_status_string(count))
        elif count == 0:
            print("error: no bytes written")
            print("  are you sure you have the right slave address?")
        elif count != len(data):
            print("error: only a partial number of bytes written")
            print("  (%d) instead of full (%d)" % (count, len(data)))

        return count

    def read_i2c(self, slave_addr, sub_addr, num_bytes_to_read=1):
        out_data = array('B', [sub_addr])
        (_ret_, num_written, in_data, num_read) = aa_i2c_write_read(self.comm, slave_addr,
                                                                    AA_I2C_NO_FLAGS, out_data,
                                                                    num_bytes_to_read)

        if num_bytes_to_read == 1:  # this is a special case, return an int rather than an array
            return in_data[0], num_read
        else:
            return in_data, num_read

    def write_spi(self, instruction, data):

        # Assemble the write command and address
        data_out = array('B', [0 for _ in range(3)])

        # instructions (2 bytes)
        data_out[0] = (instruction >> 8) & 0xff
        data_out[1] = (instruction >> 0) & 0xff  # MSB of instructions
        data_out[2] = data & 0xff  # 1 byte of data

        # Write the transaction
        (count, data_in) = aa_spi_write(self.comm, data_out, 0)
        if count < 0:
            print("error: %s\n" % aa_status_string(count))
            return
        elif count != len(data_out):
            print("error: read %d bytes (expected %d)" % (count - 3, len(data_out)))

        return data_in, count

    def read_spi(self, instruction):

        # Assemble the read command and address
        data_out = array('B', [0 for _ in range(3)])
        data_in = array('B', [0 for _ in range(3)])
        # instructions (2 bytes)
        data_out[0] = ((instruction >> 8) & 0xff) + 128  # MSB of instructions
        data_out[1] = (instruction >> 0) & 0xff  # add Read bit at bit15
        data_out[2] = 0  # container for returned data on SDO

        # Write the transaction
        (count, data_in) = aa_spi_write(self.comm, data_out, data_in)
        if count < 0:
            print("error: %s\n" % aa_status_string(count))
            return
        elif count != len(data_out):
            print("error: read %d bytes (expected %d)" % (count - 3, len(data_out)))

        # return data_in, count
        return data_in[2]

    def ask(self, interface, addr_instruction, slave_address=None,
             num_bytes_to_read=1):
        """ read a register using either SPI or i2c """

        if interface is 'SPI':
            if addr_instruction is None:
                print('Error: a SPI read needs an instruction')
                return
            return self.read_spi(addr_instruction)

        if interface is 'I2C':
            return self.read_i2c(slave_address, addr_instruction, num_bytes_to_read)[0]

    def write(self, interface, addr_instruction, data, slave_address=None):
        """ general write data over a specified interface """
        # for i2c addr_instruction is the sub_address

        if interface is 'SPI':
            return self.write_spi(addr_instruction, data)

        if interface is 'I2C':
            return self.write_i2c(slave_address, addr_instruction, data)

    def close(self):
        """ Close the device """
        aa_close(self.comm)
