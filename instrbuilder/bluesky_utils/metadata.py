# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import pandas as pd 
from databroker import list_configs, Broker
from tabulate import tabulate
from datetime import datetime
import pprint

"""
Demonstrate databroker capabilities
"""

def equivalence_check(config1, config2):

    verbose = False
    debug = False
    print('------------')
    for k1, k2 in zip(config1.keys(), config2.keys()):
        if verbose:
            print('Checking {}'.format(k1))
        if config1[k1]['data'][k1] != config2[k2]['data'][k2]:
            print('Warning!! Found configuration difference:')
            print('  Data-set 1: {} = {}'.format(k1, config1[k1]['data'][k1]))
            print('  Data-set 2: {} = {}'.format(k2, config2[k2]['data'][k2]))
        if debug:
            print('  Data-set 1: {} = {}'.format(k1, config1[k1]['data'][k1]))
            print('  Data-set 2: {} = {}'.format(k2, config2[k2]['data'][k2]))

list_configs()
db = Broker.named('local_file')
# this returns the data directory
print('Databroker config:')
pprint.pprint(db.get_config())
# --------------------------------------------------------------------
#                  Summarize the last 50 experiments
# --------------------------------------------------------------------
headers = db[-50:]  # get the last 50 headers (experiment metadata)
df = pd.DataFrame.from_dict([h.start for h in headers])  # put the run start metadata into a pandas dataframe

# Create a human-readable time index
df['human_time'] = df.apply(lambda row: datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S'), axis=1)
cols = df.columns.tolist()

# re-order the dataframe so that uid is the leftmost column
new_cols = [f for f in cols if f != 'uid']
new_cols.insert(0, 'uid')

# print out the header information with a few useful columns
df_short = df[['uid', 'human_time', 'purpose', 'plan_name', 'dut', 'num_points']]
print(tabulate(df_short, headers='keys', tablefmt='psql'))


# --------------------------------------------------------------------
#                   Demonstrate search capabilities
# --------------------------------------------------------------------

# Search for all runs with Billy as the operator
headers = db(operator='Billy')
print('Found {} runs with Billy as the operator'.format(len(list(headers))))
if len(list(headers)) > 0:
    pprint.pprint(list(headers)[0])

# Search for all runs involving ADA2200 duts
headers = db(dut='ADA2200')
print('Found {} runs with the ADA2200 as the DUT'.format(len(list(headers))))
# search results are loaded lazily and do not return a list, access via
if len(list(headers)) > 0:
    pprint.pprint(list(headers)[0]['start'])
    pprint.pprint(list(headers)[0]['descriptors']

# Search for all runs involving ADA2200 duts
headers = db(dut='ADA2200', since='2018-06-23')
print('Found {} runs with the ADA2200 as the DUT since 06-10'.format(len(list(headers))))
# search results are loaded lazily and do not return a list, access via
if len(list(headers)) > 0:
    pprint.pprint(list(headers)[0]['start'])
pprint.pprint(list(headers)[0]['descriptors'])

# for the first run let's confirm the function generator configuration
list(headers)[0]['descriptors'][0]['configuration']
# how many keys are there?
print(len(list(list(headers)[0]['descriptors'][0]['configuration'].keys())))

# what function (sine, square, triangle) was the function generator?
list(headers)[0]['descriptors'][0]['configuration']['fgen_function']['data']['fgen_function']

# TODO: dictionary of configurations seems to be doubly nested, can this be fixed?
# --------------------------------------------------------------------
#                   Instrument configuration equivalence checks
# --------------------------------------------------------------------

run1 = list(headers)[0]
run2 = list(headers)[1]

run1['descriptors'][0]['configuration']['fgen_v']['data']['fgen_v'] = 23
equivalence_check(run1['descriptors'][0]['configuration'],
                  run2['descriptors'][0]['configuration'])
