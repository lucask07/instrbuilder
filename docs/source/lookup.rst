Lookup Tables 
******************************

Instrbuilder supports lookup tables that map values sent to and received from the instrument to more human-readable intrepretations. 
Lookup tables are never required, but may ease development. The lookup table is read from `lookup.csv`.


.. csv-table:: Example of lookup table entry for the SRS810 filter slope (`filt_slope`).
	:header: command,value,name
	:widths: 7, 7, 7

	filt_slope,0,6-db/oct
	,1,12-db/oct
	,2,18-db/oct
	,3,24-db/oct