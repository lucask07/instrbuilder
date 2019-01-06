*instrbuilder* is an open-source Python package for control of electrical instruments. This package eases the development of high-level "drivers" to interface with oscilloscopes, power supplies, function generators, multimeters, or any instrument that uses ASCII textual string communication (such as SCPI [@scpi1999standard]). *instrbuilder* is particularly suited for prototying and automating experiments in research laboratory setups within an IPython terminal. Our goals are to accelerate the development of automated data collection and improve the reproducibility of laboratory experiments.

https://lucask07.github.io/instrbuilder/build/html/

###Installation Steps

1. Install a VISA driver (National Instruments provides free downloads)

2. Install *instrbuilder*

```console
username$ python -m pip instrbuilder 
```

3. If using the Bluesky suite uninstall ophyd and re-install from a git fork:

```console
username$ python -m pip uninstall ophyd 
username$ python -m pip install git+https://github.com/lucask07/ophyd@master#egg=ophyd
```

###Getting Started 

1. Command lists for Keysight oscilloscopes, function generator, DMM; Rigol DC Power Supply (*commands.csv*) are included in the package at: *instrbuilder/instruments/* 

2. Modify the example YAML file and move the ~/.instrbuilder/ OR create your own

####Create Your Own YAML

1. Initialize a YAML (specify the first parameter, the other 3 should always be default):

```python 
from instrbuilder import instrument_opening
instrument_opening.init_yaml(csv_dir = 'where/your/commands_csv/files/are',
							 cmd_name = 'commands.csv',
							 lookup_name = 'lookup.csv',
							 filename = 'config.yaml')
```

2. Add instruments using a function that prompts the user for information. Note that it may be helpful to have only one instrument connected/powered at a time so that there is no ambiguity:

```python 
from instrbuilder import instrument_opening
instrument_opening.detect_instruments()
```
