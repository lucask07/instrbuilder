* The analysis code for lock-in amplifier experiments executed with Bluesky and instrbuilder is found in this folder. 

* The data is available via figshare at: <https://doi.org/10.6084/m9.figshare.7768352>

* The analysis requires databroker, matplotlib, scipy and numpy. The matplotlib figures require latex and dvipng. Matplotlib helpers installation on Ubuntu:

```terminal 
sudo apt-get install texlive-xetex
sudo apt-get install dvipng
```

* Databroker requires a configuration file to locate the data. The data configuration file should be named *local_file.yml* to match the analysis scripts and placed within *~/.config/databroker/* A YML configuration file is available on figshare. It should look like:

```yaml
description: 'lightweight personal database'
metadatastore:
    module: 'databroker.headersource.sqlite'
    class: 'MDS'
    config:
        directory: your_directory
        timezone: 'US/Eastern'
assets:
    module: 'databroker.assets.sqlite'
    class: 'Registry'
    config:
        dbpath: 'data_directory/assets.sqlite'
```

* The script ```run_all_analysis.py``` creates each figure for the paper under review at IEEE TIM. 

* The system file open limit may need to be modified for successful completion of ```run_all_analysis.py```:
```terminal
ulimit -Sn 4095
```
