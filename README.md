[![Build Status](https://travis-ci.com/lucask07/instrbuilder.svg?branch=master)](https://travis-ci.com/lucask07/instrbuilder)
[![DOI](https://zenodo.org/badge/135353504.svg)](https://zenodo.org/badge/latestdoi/135353504)

*instrbuilder* is an open-source Python package for control of electrical instruments. This package eases the development of high-level "drivers" to interface with oscilloscopes, power supplies, function generators, multimeters, or any instrument that uses ASCII textual string communication (such as SCPI). *instrbuilder* is particularly suited for prototying and automating experiments in research laboratory setups within an IPython terminal. Our goals are to accelerate the development of automated data collection and improve the reproducibility of laboratory experiments.

## Related Journal Papers

* L. Koerner "Instrbuilder: A Python package for electrical instrument control" The Journal of Open Source Software: [doi](https://doi.org/10.21105/joss.01172)
* L. Koerner, T. Caswell, D. Allan, and S. Campbell "A Python instrument control and data acquisition suite for reproducible research" IEEE Transactions on Instrumentation and Measurement [doi](https://doi.org/10.1109/TIM.2019.2914711)


## Documentation 

https://lucask07.github.io/instrbuilder/build/html/

### Installation Steps

1. Install a VISA driver (National Instruments provides free downloads). The PyVISA documentation page is an excellent resource to locate a VISA driver for your system: 

* [NI-VISA downloads](https://pyvisa.readthedocs.io/en/stable/faq/getting_nivisa.html#faq-getting-nivisa): links to downloads separated by OS.
* [PyVISA backends](https://pyvisa.readthedocs.io/en/stable/introduction/configuring.html): an explanation of what is needed.

2. Install *instrbuilder* using pip.

```console
username$ python -m pip install instrbuilder 
```

### Getting Started 

1. Command lists for Keysight oscilloscopes, function generator, DMM; Rigol DC Power Supply (*commands.csv*) are included in the package at: [instrbuilder/instruments/](https://github.com/lucask07/instrbuilder/tree/master/instrbuilder/instruments).

Locate the instrument command files using the following python commands:

```python
import instrbuilder
init_file_loc = instrbuilder.__file__
instrument_cmds = init_file_loc.replace('__init__.py', 'instruments/')
print('Instrument commmands (csv files) are at: {}'.format(instrument_cmds))
```
Note that you can move the command csv files (and probably should). The location of these needs to be specified in the YAML configuration file.

2. A YAML file is used to track your specific system configurations and instrument addresses (e.g. USB0::0x0957::0x0407::MY44060286::INSTR). Create your system YAML file using the steps below. This will be generated at *~/.instrbuilder/* (where *~* indicates your home directory). See the [example YAML](https://github.com/lucask07/instrbuilder/blob/master/instrbuilder/example_yaml/config.yaml) on GitHub.

3. Try an example in the source code at [instrbuilder/examples/](https://github.com/lucask07/instrbuilder/tree/master/instrbuilder/examples). A Keysight and Rigol Oscilloscope is demonstrated in: [oscilloscope.py](https://github.com/lucask07/instrbuilder/blob/master/instrbuilder/examples/oscilloscope.py).

Locate the example directory using the following python commands:

```python
import instrbuilder
init_file_loc = instrbuilder.__file__
examples = init_file_loc.replace('__init__.py', 'examples/')
print('Examples are at: {}'.format(examples))
```

### Create Your YAML

1. Initialize a YAML (specify the first parameter, the other 3 should always be default):

```python 
from instrbuilder import instrument_opening
instrument_opening.init_yaml(csv_dir = 'where/your/commands_csv/files/are')
```
2. To **add instruments** to the YAML function use the script found in [instrbuilder/examples/add_instruments_to_config.py](https://github.com/lucask07/instrbuilder/blob/master/instrbuilder/examples/add_instruments_to_config.py). This will prompt the user for information. Note that it may be helpful to have only one instrument connected/powered at a time so that there is no ambiguity:

3. An example YAML is available here [on GitHub](https://github.com/lucask07/instrbuilder/blob/master/instrbuilder/example_yaml/config.yaml).

### Extra Installation Steps if Using the Bluesky Suite from NSLS-II
1. If using the Bluesky suite uninstall ophyd and re-install from a git fork:

```console
username$ python -m pip uninstall ophyd 
username$ python -m pip install git+https://github.com/lucask07/ophyd@master#egg=ophyd
```

To check if the correct *ophyd* fork was installed try:

```python
from ophyd.ee_instruments import generate_ophyd_obj
```
This warning: 

```
Error:  <class 'ImportError'>
IC (integrated circuit imports failed)
The aardvark.so or dll must be in the cwd or an importable path
Continuing anyways, since many may not use this portion...
```
is **OK**. A module import error is not.

A basic Bluesky demo is at [instrbuilder/bluesky_demo/fg_oscilloscope_basics.py](https://github.com/lucask07/instrbuilder/blob/master/instrbuilder/bluesky_demo/fg_oscilloscope_basics.py)

