Instrument Interfaces
******************************

Implemented 
==========================

* `pyvisa <https://pyvisa.readthedocs.io/en/stable/>`_: for instruments that support VISA and communicate over USB, Ethernet and GPIB.
* `pyserial <https://pythonhosted.org/pyserial/>`_: for instruments that use RS-232 or USB-to-serial interface chips

The interface and address to an instrument is passed to as a dictionary to :code:`init_instrument`

.. code-block:: python

	addr = {'pyserial': '/dev/tty.USA19H14112434P1.1'}

To-be Developed 
==========================

* `OpenCV <https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html?>`_ for cameras
* `Opal Kelly Front Panel <https://www.opalkelly.com/>`_
* `Aardvark i2c controller <https://www.totalphase.com/products/aardvark-software-api>`_ 
 