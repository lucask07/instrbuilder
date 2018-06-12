# Lucas J. Koerner
# 05/2018
# koerner.lucas@stthomas.edu
# University of St. Thomas

# standard library imports 
import sys
import os
import functools
# imports that may need installation
import matplotlib.pyplot as plt
from bluesky import RunEngine
from bluesky.callbacks import LiveTable, LivePlot
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import scan, count
from databroker import Broker

sys.path.append('/Users/koer2434/Google Drive/UST/research/bluesky/new_ophyd/') # these 2 will become an import of my ophyd
sys.path.append('/Users/koer2434/Google Drive/UST/research/bluesky/new_ophyd/ophyd/') # 
sys.path.append('/Users/koer2434/Google Drive/UST/research/instrbuilder/instrbuilder/') # this will be the SCPI library

# imports that require sys.path.append pointers 
from ophyd.signal import ScpiSignal, ScpiBaseSignal
from ophyd import Device
from ophyd.device import Kind
from scpi import init_instrument

from ophyd.areadetector.detectors import SimDetector
from ophyd.areadetector.plugins import HDF5Plugin
from ophyd.areadetector.trigger_mixins import SingleTrigger
from ophyd.areadetector.filestore_mixins import FileStoreIterativeWrite

import time
import tempfile
from pathlib import PurePath
from collections import defaultdict
import itertools
from ophyd import (BlueskyInterface, DeviceStatus, Device, Component,
                   HDF5Plugin, Staged)
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
import os
from databroker import Broker

SHAPE = (5, 5)  # shape of simulated data

db = Broker.named('temp')


class APSTriggerMixin(BlueskyInterface):
    def __init__(self, *args, image_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        if image_name is None:
            image_name = '_'.join([self.name, 'image'])
        self._image_name = image_name

    def stage(self):
        super().stage()

    def unstage(self):
        super().unstage()

    def trigger(self):
        "Trigger one acquisition."
        if self._staged != Staged.yes:
            raise RuntimeError("This detector is not ready to trigger."
                               "Call the stage() method before triggering.")

        self._status = DeviceStatus(self)
        # TODO Start the Aerotech controller and hook a callback or a Thread
        # to call self._status._finished() when it is done.

        # This will cause a Datum to be created.
        self.dispatch(self._image_name, time.time())

        super().trigger()
        return self._status


class FakeHDF5PluginWithFileStore(Device):
    filestore_spec = 'DEMO_HDF5'
    def __init__(self, *args,
                 write_path_template,
                 root=os.path.sep,
                 reg,
                 read_path_template=None,
                 **kwargs):
        super().__init__(*args, **kwargs)

        if write_path_template is None:
            raise ValueError("write_path_template is required")
        self.reg_root = root
        self.write_path_template = write_path_template
        self.read_path_template = read_path_template

        self._point_counter = None
        self._locked_key_list = False
        self._datum_uids = defaultdict(list)
        self._reg = reg

        self._filename = None
        self._resource = None

    def stage(self):
        self._point_counter = itertools.count()
        self._locked_key_list = False
        self._datum_uids.clear()
        self._filename = tempfile.NamedTemporaryFile().name
        fn = PurePath(self._filename).relative_to(self.reg_root)
        res_kwargs = {}
        self._resource = self._reg.register_resource(
            self.filestore_spec,
            str(self.reg_root), str(fn),
            res_kwargs)
        super().stage()

    def unstage(self):
        self._fn = None
        self._resource = None
        super().unstage()

    def generate_datum(self, key, timestamp, datum_kwargs):
        "Generate a uid and cache it with its key for later insertion."
        datum_kwargs = datum_kwargs or {}
        if self._locked_key_list:
            if key not in self._datum_uids:
                raise RuntimeError("modifying after lock")
        uid = self._reg.register_datum(self._resource, datum_kwargs)
        reading = {'value': uid, 'timestamp': timestamp}
        # datum_uids looks like {'dark': [reading1, reading2], ...}
        self._datum_uids[key].append(reading)
        return uid

    def describe(self):
        # One object has been 'described' once, no new keys can be added
        # during this stage/unstage cycle.
        self._locked_key_list = (self._staged == Staged.yes)
        res = super().describe()
        for k in self._datum_uids:
            res[k] = self.parent.make_data_key()  # this is on DetectorBase
        return res

    def read(self):
        # One object has been 'read' once, no new keys can be added
        # during this stage/unstage cycle.
        self._locked_key_list = (self._staged == Staged.yes)
        res = super().read()
        for k, v in self._datum_uids.items():
            res[k] = v[-1]
        return res



class FakeDetector(APSTriggerMixin, Device):
    hdf5 = Component(FakeHDF5PluginWithFileStore,
                     'HDF1:',
                     reg=db.reg,
                     write_path_template='/tmp/',
                     root='/')
    
    # This method mocks something that comes in through AreaDetector base
    # class.
    def dispatch(self, key, timestamp):
        self.hdf5.generate_datum(key, timestamp, {})
        
    # This method is just here for simulation purposes.
    # None of this should be re-used.
    def trigger(self):
        ret = super().trigger()
        import h5py
        import numpy 
        with h5py.File(self.hdf5._filename) as f:
            f.create_dataset('SOME_KEY_HERE', data=numpy.ones(SHAPE))
        self._status._finished()
        return ret

    def make_data_key(self):
        source = 'PV:{}'.format(self.prefix)
        shape = SHAPE
        return dict(shape=shape, source=source, dtype='array',
                    external='FILESTORE:')



det = FakeDetector('fake', name='det')


from bluesky import RunEngine
from bluesky.plans import count
from bluesky.callbacks.zmq import Publisher
from databroker.assets.path_only_handlers import RawHandler
from databroker.assets.core import DatumNotFound
RE = RunEngine({})
RE.subscribe(db.insert)
db.reg.register_handler('DEMO_HDF5', RawHandler)


def encode_hack(doc):
    # Avoid mutating the original and affecting any other subscribers.
    doc['data'] = doc['data'].copy()
    # Replace any datum_ids with filenames:
    for key in doc['filled']:
        for _ in range(50):
            try:
                ret = db.reg.retrieve(doc['data'][key])
                filepath, resource_kwargs, datum_kwargs = ret
                doc['data'][key] = filepath
            except DatumNotFound:
                # The database probably just doesn't have it yet.
                # Wait and try again.
                time.sleep(0.1)
            else:
                break
        else:
            raise DatumNotFound("Could not find datum_id "
                                "%s in Registry" % doc['data'][key])
    return doc 


class CustomPublisher(Publisher):
    "hack-ishly injects filename on way out"
    def __call__(self, name, doc):
        if name == 'event':
            doc = encode_hack(doc)
        print('emiited', doc)
        super().__call__(name, doc)


publisher = CustomPublisher('localhost:5567', RE=RE)  # subscribes automatically