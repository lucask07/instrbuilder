Tutorial 
**************************************************
*system setup should be completed first*

The name and address of instruments are stored in a configuration file within the user's home directory.

====================
Open an instrument
====================

.. ipython:: python

  from instrument_opening import open_by_name
  fg = open_by_name(name='old_fg')   # name within the configuration file (config.yaml)

----------------------------------------------
Simple `set` and `get` combination
----------------------------------------------

.. ipython:: python

  fg.set('offset', 0.5);
  print('Readback of Function Generator offset = {} [V]'.format(fg.get('offset')))
  fg.set('v', 1);
  fg.set('freq', 3.12e3);
  fg.set('load', 'INF');
  fg.set('output', 'ON');  # this is an example of a lookup table conversion 'ON' -> 1

Open an oscilloscope in order to demonstrate more complex setters and getters:

.. ipython:: python

  osc = open_by_name(name='msox_scope')  # name within the configuration file (config.yaml)

  osc.set('time_range', 1e-3);
  osc.set('chan_scale', 0.2, configs={'chan': 1});
  osc.set('chan_offset', 0.5, configs={'chan': 1});

Oscilloscope **triggering**

.. ipython:: python

  osc.set('trigger_sweep', 'NORM');
  osc.set('trigger_mode', 'EDGE');
  osc.set('trigger_slope', 'POS');
  osc.set('trigger_level', 0.5, configs={'chan': 1});
  osc.set('trigger_source', 1);

Oscilloscope **measurements**

.. ipython:: python

  v_average = osc.get('meas', configs={'meas_type': 'VAV', 'chan': 1});
  v_pkpk = osc.get('meas', configs={'meas_type': 'VPP', 'chan': 1});
  v_freq = osc.get('meas', configs={'meas_type': 'FREQ', 'chan': 1});

Print oscilloscope measurements 

.. ipython:: python

  print('Oscilloscope measurements: Average voltage: {} \nPeak-to-peak voltage: {}\n'.format(v_average, v_pkpk))
  print('Frequency: {} [kHz]'.format(v_freq/1000))

=========
Help 
=========
**Help** is available both at the single command level. In an iPython terminal help outputs are nicely color coded. Unfortunately, coloroma color-coding is broken in the Sphinx documentation. 

----------------------------------------------
Help on a **single command**: 
----------------------------------------------

.. ipython:: python

  fg.help('offset')
  
----------------------------------------------
Help on **all commands** (or all commands in a subsystem):
----------------------------------------------

.. ipython:: python

  fg.help_all(subsystem_list = ['output'])
