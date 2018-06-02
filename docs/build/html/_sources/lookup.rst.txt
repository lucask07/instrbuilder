Lookup Tables 
******************************

Instrbuilder commands support lookup tables that map values sent to and received from the instrument to more human-readable intrepretations. 
Lookup tables are never required, but may ease development. The lookup table is read from `lookup.csv`.

The value to be **set** can be passed as the *value* or the *name*. 
The value retrieved using **get** will always be returned as the *name*. 


.. csv-table:: Example of a lookup table entry for the SRS810 filter slope (`filt_slope`).
	:header: command,value,name
	:widths: 7, 7, 7
	:align: center

	filt_slope,0,6-db/oct
	,1,12-db/oct
	,2,18-db/oct
	,3,24-db/oct