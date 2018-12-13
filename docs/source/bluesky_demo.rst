Interfacing an Instrbuilder Instrument to Bluesky 
**************************************************

Instrbuilder is designed to interface easily with Bluesky and Ophyd from NSLS-II. 
This example is stored on _github: https://github.com/lucask07/instrbuilder/blob/master/instrbuilder/bluesky_demo/fg_oscilloscope_basics.py
-------------------------------------
Package imports
-------------------------------------
.. code-block:: python

	from bluesky import RunEngine
	from bluesky.callbacks import LiveTable
	from bluesky.plans import scan, count
	from databroker import Broker

	from ophyd.device import Kind
	from ophyd.ee_instruments import generate_ophyd_obj
	from instrument_opening import open_by_name

	RE = RunEngine({})
	db = Broker.named('local_file')  # a broker poses queries for saved data sets

	# Insert all metadata/data captured into db.
	RE.subscribe(db.insert);

-------------------------------------
Open instruments
-------------------------------------
**Open and configure the Function Generator**

.. code-block:: python

	fg_scpi = open_by_name(name='old_fg')   # name within the configuration file (config.yaml)
	fg_scpi.name = 'fg'
	FG, component_dict = generate_ophyd_obj(name='fg', scpi_obj=fg_scpi)
	fg = FG(name='fg')

	RE.md['fg'] = fg.id.get()

	# setup control of the amplitude sweep
	fg.v.delay = 0.05

	# configure the function generator
	fg.reset.set(None);  # start fresh
	fg.function.set('SIN');
	fg.load.set('INF');
	fg.freq.set(1000);
	fg.v.set(1.6);
	fg.offset.set(0);
	fg.output.set('ON');


**Open and configure the Oscilloscope**

.. code-block:: python

	osc_scpi = open_by_name(name='msox_scope')  # name within the configuration file (config.yaml)
	osc_scpi.name = 'scope'
	OSC, component_dict = generate_ophyd_obj(name='osc', scpi_obj=osc_scpi)
	osc = OSC(name='scope')

	osc.time_reference.set('CENT');
	osc.time_scale.set(200e-6);

	osc.acq_type.set('NORM');
	osc.trigger_slope.set('POS');
	osc.trigger_sweep.set('NORM');
	osc.trigger_level_chan1.set(0);
	osc.chan_scale_chan1.set(0.3);
	osc.chan_offset_chan1.set(0);
	osc.trigger_source.set(1);

--------------------------------------------------------------------------
Capture Supplemental (configuration data)
--------------------------------------------------------------------------
	
.. code-block:: python

	from bluesky.preprocessors import SupplementalData
	baseline_detectors = []
	for dev in [fg]:
	    for name in dev.component_names:
	        if getattr(dev, name).kind == Kind.config:
	            baseline_detectors.append(getattr(dev, name))

	sd = SupplementalData(baseline=baseline_detectors, monitors=[], flyers=[])
	RE.preprocessors.append(sd)

-------------------------------------
Run Bluesky Measurements
-------------------------------------

.. code-block:: python

    # sweep FG amplitude; scan is a pre-configured Bluesky plan, which steps one motor
    uid = RE(
        scan([osc.meas_vavg_chan1, osc.meas_vpp_chan1, osc.meas_freq_chan1], fg.v,
             1, 1.6, 5),
        LiveTable([fg.v, osc.meas_vavg_chan1, osc.meas_vpp_chan1, osc.meas_freq_chan1]),
        purpose='oscilloscope_function_gen_demo',
        operator='Lucas')

-------------------------------------
Investigate Data
-------------------------------------

.. code-block:: python

	header = db[uid[0]]  # db is a DataBroker instance
	print(header.table())
	df = header.table()
	# view the baseline data (i.e. configuration values)
	h = db[-1]
	df_meta = h.table('baseline')

	print('These configuration values are saved to baseline data:')
	print(df_meta.columns.values)