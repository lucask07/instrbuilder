.. instrbuilder documentation master file, created by
   sphinx-quickstart on Thu May 10 00:38:45 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

instrbuilder: Easy Instrument Control with Python
========================================================


Instrbuilder is a python library for quickly generating easy-to-use instrument high-level "drivers". The
library targets instruments that use `SCPI <https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments>`_ (Standard Commands for Programmable Instruments) 
and are interfaced to with packages such as `pyvisa <https://pyvisa.readthedocs.io/en/stable/>`_ or `pyserial <https://pythonhosted.org/pyserial/>`_. 

* **Generate a new driver** without writing python code.
* Automatic **command testing** creates reports of communication errors or unexpected return values
* **Help** sorted by subsytem 
* One-line command to capture and **save complete instrument configuration**


General Overview
=================


Index
-----

.. toctree::
   :caption: User Documentation
   :maxdepth: 1

   command
   conf
   scpi


Command Input 
=============
.. csv-table:: Example Instrument and a Single Command
  :header: name, ascii_str, ascii_str_get, getter, getter_type, setter, setter_type, setter_range, doc, subsystem, config, setter_inputs, getter_inputs, needs_development
  :widths: 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7
  
  phase, PHAS, , TRUE, float, TRUE, float, "[-360.0, 729.99]", Phase shift in degrees, ref_phase, TRUE, , ,


Help 
====


Get 
===


Set
===


Example 
=========

First, import needed modules and configure paths to the csv files of each command:

.. code-block:: python

  import os
  import scpi
  from scpi import init_instrument

  use_serial = False
  use_usb = False

  # get lockin amplifier SCPI object 
  base_dir = os.path.dirname(scpi.__file__)
  cmd_map = 'instruments/srs810/commands.csv'
  lookup = 'instruments/srs810/lookup.csv'
  lockin_addr = '/dev/tty.USA19H14112434P1.1'
   

.. ipython:: python
  :suppress:

  import os
  import scpi
  from scpi import init_instrument

  use_serial = False
  use_usb = False

  # get lockin amplifier SCPI object 
  base_dir = os.path.dirname(scpi.__file__)
  cmd_map = 'instruments/srs810/commands.csv'
  lockin_addr = '/dev/tty.USA19H14112434P1.1'


.. ipython:: python

  lia, lia_serial = init_instrument(os.path.join(base_dir, cmd_map), use_serial = use_serial, use_usb = False, addr = lockin_addr, lookup = os.path.join(base_dir, lookup))

  lia.get('phase')
  lia.set(0.1, 'phase')

  lia.help('phase')


A more complex Lock-in Amplifier set. This example requires an input dictionary configs. Here we set the lock-in display to show "R" -- magnitude.

.. ipython:: python

  lia.set(value = 1, name = 'ch1_disp', configs = {'ratio': 0})


.. module:: scpi
    :platform: Unix, MacOSX, Windows
    :synopsis: sample of documented python code

.. autofunction:: open_visa


.. autoclass:: SCPI     
   :members: 


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
