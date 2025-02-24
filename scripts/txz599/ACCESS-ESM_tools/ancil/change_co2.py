#!/usr/bin/env python3

# READ FILES
import mule
import xarray as xr

rootDir = '/g/data/p66/txz599/ACCESS-ESM_tools/ancil'
ancilFilename = f'{rootDir}/orig_co2'

# The netcdf in this example is a subset of another CO2 netCDF in which we take only the first 12 timesteps
# If you already have a 12-months CO2 netCDF to use, skip the following steps:
# ===== #
netcdfOrig = f'{rootDir}/orig_co2.nc'
d = xr.open_dataset(netcdfOrig)
netcdfFilename = f'{rootDir}/co2_new.nc'
d.co2emiss.isel(time=slice(3000,3012)).to_netcdf(netcdfFilename)
# ===== #

# Get netcdf data
netcdfFile = xr.open_dataset(netcdfFilename)
data=netcdfFile.co2emiss

# Change ancil options and data
# Load ancil file
ancilFile = mule.load_umfile(ancilFilename)
# select only first 12 fields
ancilFile.fields = ancilFile.fields[0:12]
# Change time type to 2 (Periodic time series)
ancilFile.fixed_length_header.time_type = 2
# Change validity time
ancilFile.fixed_length_header.t1_year = 0
ancilFile.fixed_length_header.t1_month = 1
ancilFile.fixed_length_header.t1_day = 16
ancilFile.fixed_length_header.t1_hour = 0
ancilFile.fixed_length_header.t1_minute = 0
ancilFile.fixed_length_header.t1_second = 0
ancilFile.fixed_length_header.t1_year_day_number = 0
ancilFile.fixed_length_header.t2_year = 0
ancilFile.fixed_length_header.t2_month = 12
ancilFile.fixed_length_header.t2_day = 16
ancilFile.fixed_length_header.t2_hour = 0
ancilFile.fixed_length_header.t2_minute = 0
ancilFile.fixed_length_header.t2_second = 0
ancilFile.fixed_length_header.t2_year_day_number = 0
# Change num of timesteps to 12
ancilFile.integer_constants.num_times = 12

# Set data
for i,d in enumerate(data):
    ancilFile.fields[i].set_data_provider(mule.ArrayDataProvider(d))
    # Change time validity
    ancilFile.fields[i].lbyr = 0
    ancilFile.fields[i].lbmon = i+1
    ancilFile.fields[i].lbdat = 16
    ancilFile.fields[i].lbhr = 0
    ancilFile.fields[i].lbmin = 0
    ancilFile.fields[i].lbsec = 0
    ancilFile.fields[i].lbyrd = 0
    ancilFile.fields[i].lbmond = i+1
    ancilFile.fields[i].lbdatd = 16
    ancilFile.fields[i].lbhrd = 0
    ancilFile.fields[i].lbmind = 0
    ancilFile.fields[i].lbsecd = 0
ancilFile.to_file(f'{rootDir}/co2_new')
