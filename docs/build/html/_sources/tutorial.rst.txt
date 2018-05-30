Tutorial 
**************************************************

Import needed modules and configure paths to the csv files of each command:

.. code-block:: python

  import os
  import yaml
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


.. ipython:: python

  import os
  import sys
  import yaml
  sys.path.append('/Users/koer2434/Google Drive/UST/research/instrbuilder/instrbuilder')
  from scpi import init_instrument

  yaml_config = open('../instrbuilder/config.yaml', 'r')
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
