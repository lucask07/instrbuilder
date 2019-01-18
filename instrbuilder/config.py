# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas
"""
Create a directory for Bluesky data; only need if using Bluesky
"""
import os
home = os.path.expanduser("~")
save_path = os.path.join(home, '.instrbuilder', 'data')

if not os.path.exists(save_path):
    os.makedirs(save_path)

class DataSave():
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

#.. todo:: file_type has no impact
data_save = DataSave(directory=save_path, file_type='.npy')
