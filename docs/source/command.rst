Command
******************************

A **command** is a gets or sets (to `value`) state of an instrument. The commands of an instrument are read from the spreadsheet: "*commands.csv*". Default values are used if a cell is left empty. 

The columns of the CSV spreadsheet are:

* **name**: The name of the command (key of the Python dictionary) 
* **ascii_str**: The string sent to the instrument upon set after the value is appended.
* **ascii_str_get**: The string sent to the instrument. Default is 'ascii_str?'
* **getter**: Is this command a getter? (bool)
* **getter_type**: Desired value returned by the getter, maps to Python conversion functions. 
* **setter**: Is this command a setter? (bool)
* **setter_type**: Expected type of the setter value.
* **setter_range**: Allowed range of the setter value. Can be a numeric list of `[min, max]` or a list of allowed options.
* **doc**: Help message. 
* **subsystem**: Subsystem of the command (simply for organizing help).
* **is_config**: Is this an instrument configuration that should be read as metadata at the start and end of every experiment? 
* **setter_inputs**: The number of setter inputs (default of 1 which is the *value*).
* **getter_inputs**: The number of getter inputs (default of 0).


Example `commands.csv`
============================

Below, portions of the the `commands.csv` file for the SRS810
digital lock-in amplifier are used to explain the format of an instrument `Command`. 

Simple Command (`phase`)
-------------------------------

.. csv-table:: Example of a simple command that uses many default values.
  :header: name, ascii_str, ascii_str_get, getter, getter_type, setter, setter_type, setter_range, doc, subsystem, is_config, setter_inputs, getter_inputs
  :widths: 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7
  
  phase, PHAS, , TRUE, float, TRUE, float, "[-360.0, 729.99]", Phase shift in degrees, ref_phase, TRUE, ,

The command `phase` is both a setter and getter. On set, 'PHAS `value`' is written to the instrument. On get, the instrument receives the query of 'PHAS?'. The value returned by the instrument is converted to a float (determined by `getter_type`). `phase` is an instrument configuration (`is_config = TRUE`) and is appropriate for logging into metadata before and after experiments. 

Complex Command (`ch1_disp`)
-------------------------------

.. csv-table:: Example of a complex command that requires a config dictionary input upon set.
  :header: name, ascii_str, ascii_str_get, getter, getter_type, setter, setter_type, setter_range, doc, subsystem, is_config, setter_inputs, getter_inputs
  :widths: 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7

  ch1_disp,DDEF {value} {ratio},DDEF?,TRUE,byte_array_to_numarray,TRUE,int,"[0, 4]","CH1 display to X, R, Xn, Aux 1or Aux 2 (j=0..4) and ratio the display to None, Aux1or Aux 2 (k=0,1,2).",disp_out,TRUE,2,

The command `ch1_disp`

Actual Class
============================


.. module:: command

.. autoclass:: Command     
   :members: 
