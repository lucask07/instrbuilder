# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas
"""
Not much here 
"""

class DataSave():
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

#TODO: file_type has no impact
data_save = DataSave(directory=save_path, file_type='.npy')