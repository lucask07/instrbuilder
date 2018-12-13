Tutorial 
**************************************************
(system setup should be completed first)

The name and address of instruments are stored in a configuration file within the user's home directory.

* Open an instrument

.. ipython:: python

  from instrument_opening import open_by_name
  fg = open_by_name(name='old_fg')   # name within the configuration file (config.yaml)

Now using the instrument object `fg` execute a simple `set` and `get` combination.

.. ipython:: python

  fg.set('offset', 0.5);
  print(fg.get('offset'))
  fg.set('v', 1);
  fg.set('freq', 3.12e3);
  fg.set('load', 'MAX');
  fg.set('output', 'ON');  # this is an example of a lookup table conversion 'ON' -> 1

Let's open an oscilloscope in order to demonstrate more complex setters and getters

.. ipython:: python

  osc = open_by_name(name='msox_scope')  # name within the configuration file (config.yaml)

  osc.set('time_range', 1e-3);
  osc.set('chan_scale', 1.2, configs={'chan': 1});
  v_average = osc.get('meas', configs={'meas_type': 'VAV', 'chan': 1});
  v_pkpk = osc.get('meas', configs={'meas_type': 'VPP', 'chan': 1});
  v_freq = osc.get('meas', configs={'meas_type': 'FREQ', 'chan': 1});

.. ipython:: python

  print('Oscilloscope measurements: Average voltage: {} \nPeak-to-peak voltage: {}\n'.format(v_average, v_pkpk))
  print('Frequency: {} [kHz]'.format(v_freq/1000))

**Help** is available both at the single command level and is color-coded nicely in an iPython terminal. Unfortunately coloroma color-coding is broken in the Sphinx documentation:

.. ipython:: python

  fg.help('offset')

And for all commands with the option to include only some subsystems:

.. ipython:: python

  fg.help_all(subsystem_list = ['output'])
