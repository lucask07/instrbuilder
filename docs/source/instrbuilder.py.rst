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
  import yaml
  import scpi

  from scpi import init_instrument

  yaml_config = open('config.yaml', 'r')
  configs = yaml.load(yaml_config)

  use_serial = False
  use_usb = False

  # get lockin amplifier SCPI object 
  commands = 'commands.csv'
  lookups = 'lookup.csv'

  instrument = 'srs810'
  cmd_map = os.path.join(configs['base_directory'], configs['csv_directory'], 
              instrument, commands)
  lookup_file = os.path.join(configs['base_directory'], configs['csv_directory'], 
              instrument, lookups)

  lockin_addr = '/dev/tty.USA19H14112434P1.1'
   

.. ansi-block:: 
Help for command [32mphase[0m in subsystem: ref_phase:
\x1b[31;1mthis is a bold red prompt> \x1b[m

.. ipython:: python
  :suppress:

  import os
  import yaml
  import scpi
  import colorama  
  import sphinx.quickstart
  colorama.init()
  from scpi import init_instrument

  yaml_config = open('../config.yaml', 'r')
  configs = yaml.load(yaml_config)

  use_serial = False
  use_usb = False

  # get lockin amplifier SCPI object 
  commands = 'commands.csv'
  lookups = 'lookup.csv'

  instrument = 'srs810'
  cmd_map = os.path.join(configs['base_directory'], configs['csv_directory'], 
              instrument, commands)
  lookup_file = os.path.join(configs['base_directory'], configs['csv_directory'], 
              instrument, lookups)

  lockin_addr = '/dev/tty.USA19H14112434P1.1'


.. ipython:: python

  lia, lia_serial = init_instrument(cmd_map, use_serial = use_serial, 
            use_usb = False, addr = lockin_addr, lookup = lookup_file, init_write = 'OUTX 0')

  lia.get('phase')
  lia.set(0.1, 'phase')

  lia.help('phase')


A more complex Lock-in Amplifier set. This example requires an input dictionary configs. Here we set the lock-in display to show "R" -- magnitude.

.. ipython:: python

  lia.set(value = 1, name = 'ch1_disp', configs = {'ratio': 0})

.. ipython:: python:: ansi-block

  import readline
  import colorama
  import sphinx.quickstart
  colorama.init()
  import sys
  print(sys.version)
  import IPython
  print("This IPython is version:",IPython.__version__)


  print("\x1b[31;1mthis is a bold red prompt> \x1b[m")


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
