#!/usr/bin/env python3

# READ FILES
import mule
import xarray as xr

ancilFilename = 'CO2_fluxes_ESM_1750_2014.anc'

# Get netcdf data
netcdfFilename = 'co2.nc'
netcdfFile = xr.open_dataset(netcdfFilename)
data=netcdfFile.co2emiss

# Change ancil options and data
ancilFile = mule.load_umfile(ancilFilename)
ancilFile.fields = [ancilFile.fields[0]]
ancilFile.fixed_length_header.time_type = 0
ancilFile.fields[0].set_data_provider(mule.ArrayDataProvider(data))
ancilFile.to_file(f'{ancilFilename}_new')
