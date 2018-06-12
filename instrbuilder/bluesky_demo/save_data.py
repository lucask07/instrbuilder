import pandas as pd 
import os

# Save data (data-frames) to two other formats: csv and hdf5
#	ALTHOUGH this is not needed and the .sqlite is file is the most complete 
# See: https://pandas.pydata.org/pandas-docs/stable/io.html
default_data_dir = os.getcwd()

def to_csv(df, filename, data_dir = default_data_dir):
    """ 
    Saves panda data-frame to csv and organizes filename and directory 

    Parameters
    ----------
    df : pandas data-frame    
    filename : string
        filename 
    data_dir : string, optional
    	directory for data to be saved
    Returns
    -------
    None
    """

	filename = 'test_data_{}.csv'.format(filename)
	fullfile = os.path.join(data_dir, filename)
	print('saving table as: {}'.format(filename))
	print(' to directory: {}'.format(data_dir))
	df.to_csv(fullfile)

def to_hdf(uid, df, data_dir = default_data_dir):
    """ 
    Saves panda data-frame to hdf and organizes filename and directory 

    Parameters
    ----------
    df : pandas data-frame    
    filename : string
        filename 
    data_dir : string, optional
    	directory for data to be saved
    Returns
    -------
    None
    """

	filename = 'test_data_{}.hdf'.format(filename)
	fullfile = os.path.join(data_dir, filename) #TODO: what does the hdf key do?
	print('saving table as: {}'.format(filename))
	print(' to directory: {}'.format(data_dir))
	df.to_hdf(fullfile, key = 'test_id')

# the location of the data database and the json metadata files is set by the config file 'local_file'
# 	db = Broker.named('local_file') 
# this .yml config file (on my system) is at ~/.config/databroker
# each run of the run-engine makes an sqlite data file; 
# 	all JSON metadata/headers (start; stop; event_descriptors) are in the same .json file


# prettry print json from terminal
# cat run_starts.json | json_pp

