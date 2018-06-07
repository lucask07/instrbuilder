Tutorial 
**************************************************

Import needed modules and configure paths to the CSV file that describes the commands of the instrument:

.. code-block:: python

  import os
  import yaml
  from scpi import init_instrument

  yaml_config = open('config.yaml', 'r')
  configs = yaml.load(yaml_config)

  # get paths to the lockin amplifier CSV files 
  commands = 'commands.csv'
  lookups = 'lookup.csv'
  instrument = 'srs810'

  cmd_map = os.path.join(configs['base_directory'], configs['csv_directory'], 
              instrument, commands)
  lookup_file = os.path.join(configs['base_directory'], configs['csv_directory'], 
              instrument, lookups)

  # configure the transport method (pyserial) and the device address        
  addr = {'pyserial': '/dev/tty.USA19H14112434P1.1'}


.. ipython:: python
  :suppress:

  import os
  import yaml
  from scpi import init_instrument

  yaml_config = open('../instrbuilder/config.yaml', 'r')
  configs = yaml.load(yaml_config)

  # get lockin amplifier CSV paths
  commands = 'commands.csv'
  lookups = 'lookup.csv'

  instrument = 'srs810'
  cmd_map = os.path.join(configs['base_directory'], configs['csv_directory'], 
              instrument, commands)
  lookup_file = os.path.join(configs['base_directory'], configs['csv_directory'], 
              instrument, lookups)

  # configure the transport method (pyserial) and the device address
  addr = {'pyserial': '/dev/tty.USA19H14112434P1.1'}

Initialize the instrument object `lia` and execute a simple `get` and `set`.

.. ipython:: python

  lia, lia_serial = init_instrument(cmd_map, addr = addr,
    lookup = lookup_file, init_write = 'OUTX 0')

  print(lia.get('phase'))
  ret = lia.set(0.1, 'phase')


A more complex Lock-in Amplifier `set`. This example requires an input dictionary `configs`. Here we set the lock-in display to show "R" -- magnitude (using the lookup-table).


.. ipython:: python

  ret = lia.set(value = 'R', name = 'ch1_disp', configs = {'ratio': 0})

  # note the ASCII string of this command shows:
  print(lia._cmds['ch1_disp'].ascii_str)

  lia.help('ch1_disp')


**Help** is available both at the single command level and is color-coded nicely in an iPython terminal. Unfortunately coloroma color-coding is broken in the Sphinx documentation:

.. ipython:: python

  lia.help('phase')

And for all commands with the option to include only some subsystems:

.. ipython:: python

  lia.help_all(subsystem_list = ['input_filter'])
