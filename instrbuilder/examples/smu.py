# Lucas J. Koerner
# 06/2025
# koerner.lucas@stthomas.edu
# University of St. Thomas

from instrbuilder.instrument_opening import open_by_name
import time

smu = open_by_name(name='smu')   # name within the configuration file (config.yaml)

smu.get('v', configs={'chan': 1})
smu.get('i', configs={'chan': 1})

smu.get('v', configs={'chan': 2})
smu.get('i', configs={'chan': 2})

smu.set('v', 2.35, configs={'chan': 2})
smu.set('output', 1, configs={'chan': 2})

time.sleep(2)
smu.get('output', configs={'chan': 2})
