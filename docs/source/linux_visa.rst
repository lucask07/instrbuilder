VISA Installation on Linux
******************************

The National Instruments VISA driver does not support certain Linux distributions, specifically Ubuntu. The `pyvisa-py <https://pyvisa.readthedocs.io/en/latest>`_ VISA backend is pure Python and can be used to run PyVISA and *instrbuilder* on Ubuntu.

The installation steps are as follows:

.. code-block:: console

	username$ python -m pip install pyvisa-py
	username$ python -m pip install pyusb 

Check VISA status: 

.. code-block:: console

	username$ python -m visa info


Ubuntu requires "rules" to be added for a user to fully access the USB device. 

Add the following line to /etc/udev/rules.d/99-com.rules:

.. code-block:: console

	SUBSYSTEM=="usb", MODE="0666", GROUP="usbusers"

Create the 99-com.rules file if necessary.

Then add your user to the usbusers group

.. code-block:: console

	sudo groupadd usbusers
	sudo usermod -a -G usbusers USERNAME

Reboot your system

Finally check to see if you can detect a USB connected instrument using PyVISA:

.. code-block:: python

	import visa
	rm = visa.ResourceManager('@py')
	address = rm.list_resources()

If the Python code returns a device address you are now good to go!


For more info regarding USB permissions and the udev rules see `this stackoverflow question <https://stackoverflow.com/questions/52256123/unable-to-get-full-visa-address-that-includes-the-serial-number>`_

