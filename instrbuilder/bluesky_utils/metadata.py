# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

import pandas as pd 
from databroker import list_configs, Broker
from tabulate import tabulate
from datetime import datetime

"""
Demonstrate generation of a table of header information labeled by uid 
"""
list_configs()
db = Broker.named('local_file')
headers = db[-1000:] # need a better way to get all the headers  
df = pd.DataFrame.from_dict([h.start for h in headers])

# Create a human-readable time index 
df['human_time'] = df.apply(lambda row: datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S'), axis=1)
cols = df.columns.tolist()

# for aesthetics, re-order the dataframe so that uid is the leftmost column
new_cols = [f for f in cols if f != 'uid']
new_cols.insert(0, 'uid')

# print out the header information with a few useful columns
df_short = df[['uid', 'human_time', 'plan_pattern']]
print(tabulate(df_short, headers='keys', tablefmt='psql'))