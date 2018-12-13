Adding Instruments  
**************************************************

The name and address of instruments are stored in a configuration file within the user's home directory (~/.instrbuilder/config.yaml).


=======================================
Intialize YAML 
=======================================
only required if a YAML file does not yet exist!! 

.. code-block:: python

  from instrument_opening import init_yaml, detect_instruments
  init_yaml(csv_dir, cmd_name, lookup_name, filename = 'config.yaml')


=======================================
Detect Instruments
=======================================

it may help to run detect_instruments with only 1 instrument at a time turned on

.. code-block:: python

  detect_instruments()

*detect_instruments()* requests user input to configure the YAML file


The **resulting** *config.yaml* file looks like:

.. code-block:: yaml

  csv_directory: /Users/koer2434/Google Drive/UST/research/instrbuilder/instruments
  cmd_name: commands.csv
  lookup_name: lookup.csv
  instruments:
    old_fg:
      address:
        pyvisa: USB0::0x0957::0x0407::MY44060286::INSTR
      python_class: KeysightFunctionGen
      csv_folder: keysight/function_gen/33500B