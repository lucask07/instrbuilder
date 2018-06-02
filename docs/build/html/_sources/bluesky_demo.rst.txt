Interfacing an Instrbuilder Instrument to Bluesky 
**************************************************

Instrbuilder is designed to interface easily with Bluesky and Ophyd from NSLS-II. An example is shown below where *Ophyd* signals are created from an *Instrbuilder* instrument object and command name using :code:`ScpiSignal` and 
:code:`ScpiBaseSignal`.

.. code-block:: python

	from scpi import init_instrument
	from ophyd.signal import ScpiSignal, ScpiBaseSignal

	lia, lia_serial = init_instrument(cmd_map, addr = addr,
		lookup = lookup_file, init_write = 'OUTX 0')
	fg, fg_usb = init_instrument(cmd_map, addr = addr,
		lookup = lookup_file)

	# setup the Bluesky "motor"
	freq_motor = ScpiSignal(fg, 'freq')
	freq_motor.delay = 0.1

	# Add the Bluesky "detector" from the lock-in amplifier  
	det = ScpiBaseSignal(lia, 'disp_val')

	# run a scan that linearly steps the function generator frequency from 
	# 4.997 kHz to 5.005 kHz and reads the lock-in detector magnitude 
	uid = RE(scan([det], freq_motor, 4997, 5005, 12), 
		LiveTable([det]), attenuator='0dB', purpose='demo', operator='Lucas')


**ToDo**: Next time in lab have this display the actual LiveTable results. 