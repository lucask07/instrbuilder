.. instrbuilder documentation master file, created by
   sphinx-quickstart on Thu May 10 00:38:45 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

instrbuilder: INSTRUMENT BUILDER
========================================================


Instrbuilder is a python library for quickly generating easy to use instrument drivers. The
library targets instruments that use `SCPI <https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments>`_ (Standard Commands for Programmable Instruments) 
and are interfaced to with packages such as pyvisa or pyserial. 

* **Generate a new driver** without writing python code.
* **Rich Metadata:** Captured and organized to facilitate reproducibility and
  searchability.

::fg.set(0, 'offset')


.. code-block:: python

   def some_function():
       interesting = False
       print('This line is highlighted.')
       print('This one is not...')
       print('...but this one is.')


.. ipython:: python

    def t(a, b):
        return a + b

    t(14, 2)

.. ipython:: python

    import os
    import sys
    cwd = os.getcwd()
    print(cwd)
    print(os.path.abspath(os.getcwd() + os.sep + os.pardir))
    sys.path.insert(0, os.path.abspath(os.getcwd() + os.sep + os.pardir))
	import scpi

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. todo:: This is a simple, stand-alone todo not linked to code

.. class:: Commmand


.. module:: scpi
    :platform: Unix, MacOSX, Windows
    :synopsis: sample of documented python code

.. autofunction:: open_visa


.. autoclass:: SCPI     
   :members: 

.. module:: command


.. autoclass:: Command     
   :members: 


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
