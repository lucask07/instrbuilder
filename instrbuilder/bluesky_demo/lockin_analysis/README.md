The analysis code for lock-in amplifier analysis run with Bluesky and instrbuilder is found in this folder. 

The data is available via figshare at: 
[data repository link](https://figshare.com/s/ce1554937c4adc2f1de2)

Once publised the dataset will have a DOI of: <10.6084/m9.figshare.7768352>

The analysis requires databroker, matplotlib, scipy and numpy. 

To setup a databroker configuration to point to the directory that stores the data refer to:
[Data broker configurations](http://nsls-ii.github.io/databroker/configuration.html)

The database configuration file should be named *local_file.yml* to match the analysis scripts. The file contents should be:

```yaml
description: 'lightweight personal database'
metadatastore:
    module: 'databroker.headersource.sqlite'
    class: 'MDS'
    config:
        directory: '/Users/koer2434/Google Drive/UST/research/bluesky/data'
        timezone: 'US/Eastern'
assets:
    module: 'databroker.assets.sqlite'
    class: 'Registry'
    config:
        dbpath: '/Users/koer2434/Google Drive/UST/research/bluesky/data/assets.sqlite'
```

The script ```run_all_analysis.py``` creates each figure for the paper under review at IEEE TIM. 


