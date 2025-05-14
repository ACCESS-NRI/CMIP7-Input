# Produce atmosphere restart for ESM1.6

Creates a new restart file, based on an old restart file. The vegetation fractions in this original restart file are not congruent with the LUH3 data. A new vegetation map which is congruent with the LUH3 data was created by Rachel Law at "/g/data/p66/rml599/luh2/luh3/restart-fields/newvegfrac.1850.nc".

The process is comprised of 3 scripts:

1. convert_UM_restart_to_netcdf.py- converts all the CABLE fields (which is defined as all fields which have a pseudo-level dimension of 17) to NetCDF, replacing all instances of ```/``` with ``` PER ```, as the ```/``` is not allowed in NetCDF names.
2. remap_vegetation.py- performs the remapping of restart fields for the new vegetation map. Detailed description of the script below.
3. add_netcdf_fields_to_UM_restart.py- take the generataed NetCDF file from ```remap_vegetation.py``` and copy the variables into their respective restart fields.

These are executed via ```run_remap.sh```. The current configuration in ```run_remap.sh``` should work out of the box.
## remap_vegetation.py

The ACCESS-ESM1.5 restart only contains physically valid values on active tiles i.e. tiles that have non-zero fraction in the grid cell at some point during the LUC dataset. Thus changing the vegetation map requires major changes to all tiled values in the restart. There are two "types" of tiled variables which should be treated differently.

The vegetation agnostic variables, like soil moisture and temperature. These variables are not required to be kept distinct across tiles. In this case, all tiles are given the fraction weighted cell average e.g. in the original restart, a cell has tile 1 with area fraction 0.75 and soil temperature of 300K, tile 2 with area fraction of 0.25 and soil temperature of 305K, the new soil temperature of all tiles on the cell would be 300*0.75 + 305 * 0.25. 

The vegetation specific variables, primarily the nutrient pools. These variables should remain distinct across tiles. The fill process is as follows:

1. Identified valid vegetation type mappings from the old vegetation types to the new. For most vegetation types, this is a 1-to-1 relationship i.e. only vegetation type 1 is valid for filling vegetation type 2, type 2 is valid for type 2 etc. For instances of new vegetation types being added, it is possible to map existing types to the new type, so that new types get an average of the types that were mapped to it. For example, in ESM1.6, C4 grasses (type 10) were added as a vegetation type, which was not included in ACCESS-ESM1.5. Vegetation types 6, 7 and 9 were considered valid vegetation types to fill the C4 grasses.

Following steps are applied at every tile on all land grid cell:

2. Check if the old vegetation surface fractions contained non-zero fraction of a vegetation type valid for the current tile. If yes, then the new value is set to the old value on that tile (non-weighted average if multiple valid vegetation types have non-zero fraction, as with C4 grasses). If not, continue to stage 3.

3. Check for valid vegetated tiles in a small area around the original cell, where the area is defined by a number of latitude and longitude indices either side of the original cell. If any valid tiles exist, then take the non-weighted average of all valid tiles. If no valid tiles exist, continue to step 4. In this instance, 2 cells either side are used (i.e. a 5x5 square of cells around the original cell).

4. Check for valid vegetation tiles in a latitude band around the original cell. If any valid tiles exist, then take the non-weighted average of all valid tiles. If no tiles exist, then continue to step 5. The latitude band is this instance is 8 cells either side (+- 10 degrees).

5. Check for valid vegetation tiles globally. If any valid tiles exist, then take the non-weighted average of all valid tiles. If no tiles exist, then set the value to 0.0.

The vegetation specific and vegetation agnostic fields are specified in the config file, which is passed as the --config(-c) command line argument.
