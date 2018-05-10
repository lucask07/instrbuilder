.. instrbuilder documentation master file, created by
   sphinx-quickstart on Tue May  8 09:44:04 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to instrbuilder's documentation!
========================================

INSTRUMENT BUILDER -- EASY CONTROL DRIVERS
===========================================

Instrbuilder is a python library for quickly generating easy to use instrument drivers. The
library targets instruments that use SCPI (Standard Commands for Programmable Instruments) 
and can be interfaced to with packages such as pyvisa or pyserial. 

* **Generate a new driver** without writing python code.
* **Rich Metadata:** Captured and organized to facilitate reproducibility and
  searchability.

open a function generator and run 
.. code:: python

    from time import sleep
    import datetime
    now = datetime.datetime.now
    from bluesky import Msg


`EPICS <http://www.aps.anl.gov/epics/>`_. Other control systems could be
integrated with bluesky in the future by presenting this same interface.

.. toctree::
   :caption: Developer Documentation
   :maxdepth: 1

   command
   scpi
   run_engine
   api_changes


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   csv
   lookup

.. currentmodule:: instrbuilder.scpi

:func:`conv_arr_str`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
