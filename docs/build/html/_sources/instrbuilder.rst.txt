.. instrbuilder documentation master file, created by
   sphinx-quickstart on Thu May 10 00:38:45 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Instrbuilder: Easy Instrument Control with Python
**************************************************
Instrbuilder is a Python library for quickly generating easy-to-use instrument high-level "drivers". The
library targets instruments that commuicate with simple read/write of strings, such as `SCPI <https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments>`_ (Standard Commands for Programmable Instruments), 
and are interfaced to with Python packages such as `pyvisa <https://pyvisa.readthedocs.io/en/stable/>`_ or `pyserial <https://pythonhosted.org/pyserial/>`_. Instrbuilder is designed to integrate with the Python experiment control and acquisition library created at the `NSLS-II <https://nsls-ii.github.io/>`_. The NSLS-II library supports thousands of users at large national x-ray sources; here we adapt and demonstrate the NSLS-II library for small laboratories (a couple of users).

Instrbuilder allows you to:

* **Generate a new driver** without writing python code.
* **Automatically test commands** and create reports of communication errors or unexpected return values.
* **View help** on each command sorted by subsytem. 
* **Capture and save complete instrument configurations**. 
* **Seamlessly utilize the NSLS-II** `Bluesky <https://nsls-ii.github.io/>`_ experiment control and acquisition library.


Documentation Table of Contents 
=================================


.. toctree::
   :caption: User Documentation
   :maxdepth: 1

   tutorial
   example_instrument
   scpi
   command_testing


.. toctree::
   :hidden:
   :caption: NSLS-II Data Collection

   bluesky <https://nsls-ii.github.io/bluesky>
   ophyd <https://nsls-ii.github.io/ophyd>

.. toctree::
   :hidden:
   :caption: NSLS-II Data Access and Management

   databroker <https://nsls-ii.github.io/databroker>



Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
