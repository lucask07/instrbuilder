# Lucas J. Koerner
# 2019
# koerner.lucas@stthomas.edu
# University of St. Thomas

from bluesky_utils.metadata import equivalence_check
from databroker import Broker

try:
    db
except NameError:
    db = Broker.named('local_file') # a broker poses queries for saved data sets

purpose = 'snr_SR810'
headers=db(purpose=purpose) 
print('Found {} runs with the purpose of {}'.format(len(list(headers)), purpose))
run1 = list(headers)[18]  
run2 = list(headers)[23]

print('Comparing: \n  UID = {} to \n  UID = {}'.format(run1['start']['uid'], 
	run2['start']['uid']))

equivalence_check(run1['descriptors'][0]['configuration'], 
	run2['descriptors'][0]['configuration'])  