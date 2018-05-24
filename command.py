# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas


# standard library imports 
import ast
import math
import re
import warnings
import time
from collections import defaultdict
import sys

# imports that may need installation
import colorama
import pandas as pd
import numpy as np
import serial
import visa

"""

"""

class Command(object):
    """
    A command to be sent to an instrument 

    .. todo::

       * Determine if the command is a SCPI comms error flag
       * Add a switch to enable or disable the lookup table 
       * defaults for long getters and setters
       * long getters/setters: need range requirements and names for 2nd and beyond getter inputs
       * long getter returns:  have custom getter_type functions, need to test
       * input files: 1) extra getter/setter inputs; 2) range for extra inputs


    Parameters
    ----------
    name : string
        The name of the command, used as lookup key 
        to the instrument's dictionary of commands
    ascii_str : string
        What is sent to the instrument
    ascii_str_get : string, optional
        What is sent to the instrument when getting a value.
        If not specified ascii_str will be used 
    getter : Boolean 
        Is this command a getter?
    getter_type : function, float
        Converts the instrument returned value to a new type for processing
        Example: float
    setter : Boolean 
        Is this command a setter?
    setter_range : list
        Minimum and maximum allowed values for the set operation
    setter_type : function, float
        Currently not used; may be used to check if set value is the proper type 
    doc : string, optional
        Documentation for this command; will be printed with help
    subsystem : string, optional
        The subsystem (of the instrument) that this command fits into
        Used for organization help information
    getter_inputs : list (of strings)
        For non-conventional get functions (long getters) that send extra parameters.
        This is a list of the input parameters that are needed. These are keys to 
        the config dictionary
    setter_inputs : list (of strings)
        For non-conventional set functions (long setters) that send extra parameters (beyond 'value').
        This is a list of the input parameters that are needed. These are keys to 
        the config dictionary
    lookup : dictionary 
        A lookup table for values that can be mapped to more human-readable results. 
        E.g. lookup = `{'SLOW': 0, 'FAST': 1}`
        The keys are the human-readable names, the dictionary values are what is sent and 
        received from the instrument. 
    """

    def __init__(self, name, ascii_str='', ascii_str_get='',
                 getter=True, getter_type=float,
                 setter=True, setter_range=None, setter_type=float,
                 doc='', subsystem=None,
                 getter_inputs=None, setter_inputs=None,
                 lookup={}):

        self.name = name

        ascii_str = ascii_str.rstrip()
        if ascii_str.find('{value}') == -1:
            # command that is sent over scpi
            self.ascii_str = ascii_str + ' {value}'
        else:
            self.ascii_str = ascii_str

        if ascii_str_get is None:
            # for most cases replace the value with ?
            self.ascii_str_get = self.ascii_str.replace(' {value}', '?')
        else:
            self.ascii_str_get = ascii_str_get

        # put the get command configuration keys into a list
        self.get_config_keys = re.findall(r'{\s*(.*?)\s*}', self.ascii_str_get)
        self.set_config_keys = re.findall(r'{\s*(.*?)\s*}', self.ascii_str)
        # value is special, not a configuration key; it is always required input to setter
        #   (value must be set to None if a "setter" that does not send a value is needed)
        self.set_config_keys.remove('value')
        self.get_config_defaults = dict.fromkeys(self.get_config_keys)
        self.set_config_defaults = dict.fromkeys(self.set_config_keys)

        self.getter = getter    # is this a getter? True or False
        
        # getter_type: a function that converts the value retrieved to the anticipated type,
        # typically a built-in like float, int, etc. but could be a custom function
        self.getter_type = getter_type
        self.setter = setter            # is this a setter? True or False
        self.setter_type = setter_type  # TODO: checks that the value matches this type
        self.setter_range = setter_range
        self.doc = doc
        self.subsystem = subsystem
        self.getter_inputs = getter_inputs
        self.setter_inputs = setter_inputs

        # lookup table support (dictionary)
        self.lookup = lookup