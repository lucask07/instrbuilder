*instrbuilder* is an open-source Python package for control of electrical instruments. This package eases the development of high-level "drivers" to interface with oscilloscopes, power supplies, function generators, multimeters, or any instrument that uses ASCII textual string communication (such as SCPI [@scpi1999standard]). *instrbuilder* is particularly suited for prototying and automating experiments in research laboratory setups within an IPython terminal. Our goals are to accelerate the development of automated data collection and improve the reproducibility of laboratory experiments.

## Documentation 

https://lucask07.github.io/instrbuilder/build/html/

### Installation Steps

1. Install a VISA driver (National Instruments provides free downloads). The PyVISA backend documentation page is an excellent resource to locate a VISA driver for your system: [PyVISA backends](https://pyvisa.readthedocs.io/en/stable/getting.html#backend)

2. Install *instrbuilder*

```console
username$ python -m pip instrbuilder 
```

### Getting Started 

1. Command lists for Keysight oscilloscopes, function generator, DMM; Rigol DC Power Supply (*commands.csv*) are included in the package at: *instrbuilder/instruments/*.
To find the location of the instrument command files run the following python commands:

```python
import instrbuilder
init_file_loc = instrbuilder.__file__
instrument_cmds = init_file_loc.replace('__init__.py', 'instruments/')
examples = init_file_loc.replace('__init__.py', 'examples/')
print('Instrument commmands (csv files) are at: {}'.format(instrument_cmds))
```

2. A YAML file is used to track your specific system configurations and instrument addresses (e.g.USB0::0x0957::0x0407::MY44060286::INSTR). Modify the example YAML file and move to ~/.instrbuilder/ OR create your own

3. Try an example in the source code at *instrbuilder/examples/*. A Keysight and Rigol Oscilloscope is demonstrated in: *oscilloscope.py*.

Locate the example directory using the following code:

```python
import instrbuilder
init_file_loc = instrbuilder.__file__
examples = init_file_loc.replace('__init__.py', 'examples/')
print('Examples are at: {}'.format(examples))
```

### Create Your Own YAML

1. Initialize a YAML (specify the first parameter, the other 3 should always be default):

```python 
from instrbuilder import instrument_opening
instrument_opening.init_yaml(csv_dir = 'where/your/commands_csv/files/are')
```
2. **Add instruments** to the YAML function use the script found in instrbuilder\examples\add_instruments_to_config.py. This will prompt the user for information. Note that it may be helpful to have only one instrument connected/powered at a time so that there is no ambiguity:

### Extra Installation Steps if Using the Bluesky Suite from NSLS-II
3. If using the Bluesky suite uninstall ophyd and re-install from a git fork:

```console
username$ python -m pip uninstall ophyd 
username$ python -m pip install git+https://github.com/lucask07/ophyd@master#egg=ophyd
```

The check if the correct *ophyd* fork was installed try:

```python
from ophyd.ee_instruments import generate_ophyd_obj
```

A basic Bluesky demo is at *instrbuilder/

