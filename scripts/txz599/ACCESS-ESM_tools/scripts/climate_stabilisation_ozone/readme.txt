#
Scripts for creating time-sliced ozone ancillary files for ACCESS-ESM1.5.

Specifically created for use in the CMIP6-adjacent climate 
stabilisation simulations based on SSP585.

Scripts by Chloe Mackallah and Martin Dix, CSIRO.

This task was split into two scripts because the modules refused to play nice with each other.

##############################

DESCRIPTION:

Scripts come in 2 parts:

1. extract_ozone_year_pt1.sh extracts the timesliced data and creates temporary
   netCDF files with appropriate data.

2. extract_ozone_year_pt2.sh converts the temp netCDF files into UM anc file format.

NOTE: The variables 'year' and 'outfile' must be set in BOTH scripts to be exactly the same.


TO RUN:

Once the two variables are correctly set, simple run them consecutively from the command line; i.e.:

$ ./extract_ozone_year_pt1.sh
$ ./extract_ozone_year_pt2.sh

And the final ESM-ready ancil file will be contained in a subdirectory named after the 'year' variable.

