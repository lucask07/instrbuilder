# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

from instrument_opening import open_by_name
import time

pwr = open_by_name(name='rigol_pwr1')   # name within the configuration file (config.yaml)


pwr.get('v', configs={'chan': 1})
pwr.get('i', configs={'chan': 1})

pwr.get('v', configs={'chan': 2})
pwr.get('i', configs={'chan': 2})

pwr.set('v', 0.1, configs={'chan': 2})
pwr.set('ovp', 1.5, configs={'chan': 2})

pwr.set('ocp', 0.07, configs={'chan': 2})

pwr.set('out_state', 'ON', configs={'chan': 1})
time.sleep(2)
pwr.set('out_state', 'OFF', configs={'chan': 1})

pwr.get('meas_i', configs={'chan': 1})

pwr.get('meas_v', configs={'chan': 1})

