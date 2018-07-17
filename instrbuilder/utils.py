# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import visa


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
