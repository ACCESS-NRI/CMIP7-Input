#!/usr/bin/env python3

# READ FILES
import mule
import xarray as xr

rootDir = '/g/data/p66/txz599/ACCESS-ESM_tools/ancil/co2_emissions_ts'
ancilFilename = f'{rootDir}/orig_co2'
netcdfFilename = f'{rootDir}/co2_cdr_NH.nc'
start_yr = 200
end_yr = 400

# Get netcdf data
print("Opening data...")
netcdfFile = xr.open_dataset(netcdfFilename)
data=netcdfFile['co2emiss'] #name of the data in your netCDF

# We create a suitable netcdf in this example (100 years of monthly data)
# If you already have a suitable netCDF to use, skip the following steps:
# ===== #
#print("Creating data...")
#import numpy as np
#from datetime import datetime as dt
# Create time coord
#time = [dt(y,m,16) for m in range(1,13) for y in range(start_yr,end_yr+1)]
# Create monthly data based on start and end years
#data = xr.apply_ufunc(lambda d: np.tile(d,(end_yr-start_yr+1,1,1)),data,
#    input_core_dims=[['time','lat','lon']],
#    exclude_dims=set(['time']),
#    output_core_dims=[['time','lat','lon']],
#    ).assign_coords({'time':time})
# ===== #

BMDI = -2.0**30 # (-1073741824.0) Value used in the UM Fieldsfile to indicate NaN
print("Changing values...")
# Change NaNs to BMDI
data = data.where(~data.isnull(),BMDI)

# Change ancil options and data
# Load ancil file
ancilFile = mule.load_umfile(ancilFilename)
# Set calendar to BMDI (any calendar)
# Since it's a monthly series it is suitable for any
# calendar among Proleptic Gregorian, 360-day, and 365-day)
ancilFile.fixed_length_header.calendar = 1
# Set time type to 1 (Time series)
ancilFile.fixed_length_header.time_type = 1
# Change validity time
ancilFile.fixed_length_header.t1_year = start_yr
ancilFile.fixed_length_header.t1_month = 1
ancilFile.fixed_length_header.t1_day = 16
ancilFile.fixed_length_header.t1_hour = 0
ancilFile.fixed_length_header.t1_minute = 0
ancilFile.fixed_length_header.t1_second = 0
ancilFile.fixed_length_header.t1_year_day_number = 0
ancilFile.fixed_length_header.t2_year = end_yr
ancilFile.fixed_length_header.t2_month = 12
ancilFile.fixed_length_header.t2_day = 16
ancilFile.fixed_length_header.t2_hour = 0
ancilFile.fixed_length_header.t2_minute = 0
ancilFile.fixed_length_header.t2_second = 0
ancilFile.fixed_length_header.t2_year_day_number = 0
# Change num of timesteps to len(time)
ancilFile.integer_constants.num_times = len(data.time)

# Set ancillary file fields as a copy of first field
ancilFile.fields = [ancilFile.fields[0].copy() for _ in data.time]
# Write data
print("Writing fields...")
for i,d in enumerate(data):
    ancilFile.fields[i].set_data_provider(mule.ArrayDataProvider(d))
    # Change time validity
    ancilFile.fields[i].lbyr = start_yr + i//12
    ancilFile.fields[i].lbmon = i%12+1
    ancilFile.fields[i].lbdat = 1
    ancilFile.fields[i].lbhr = 0
    ancilFile.fields[i].lbmin = 0
    ancilFile.fields[i].lbsec = 0
    ancilFile.fields[i].lbyrd = 0
    ancilFile.fields[i].lbmond = 0
    ancilFile.fields[i].lbdatd = 0
    ancilFile.fields[i].lbhrd = 0
    ancilFile.fields[i].lbmind = 0
    ancilFile.fields[i].lbsecd = 0
ancilFile.to_file(f'{rootDir}/co2_tseries_new')
print('Done!')
