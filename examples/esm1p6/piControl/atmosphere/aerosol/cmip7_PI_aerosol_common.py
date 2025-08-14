import numpy as np
import ants
import ants.io.save as save
import mule
import iris
import cftime, cf_units
from pathlib import Path
import os, tempfile

mask_esm15 = iris.load_cube('/g/data/vk83/configurations/inputs/access-esm1p5/modern/share/atmosphere/grids/global.N96/2020.05.19/qrparm.mask')
mask_esm15.coord('latitude').guess_bounds()
mask_esm15.coord('longitude').guess_bounds()

interpolation_scheme = iris.analysis.AreaWeighted(mdtol=0.5)

# For CMIP6 and CMIP7 data
t1 = cftime.DatetimeNoLeap(1850,1,1)
t2 = cftime.DatetimeNoLeap(1850,12,31)
constraint_1850 = iris.Constraint(time=lambda cell: t1 <= cell.point < t2)

def cmip7_path(var):
    base  = Path('/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/PNNL-JGCRI/CEDS-CMIP-2025-03-18/atmos/mon')
    return base / f'{var}_em_anthro/gn/v20250325/{var}-em-anthro_input4MIPs_emissions_CMIP_CEDS-CMIP-2025-03-18_gn_185001-189912.nc'

def load_cmip7_1850_aerosol(type):
    cube = iris.load_cube(cmip7_path(type), constraint_1850)
    fix_coords(cube)
    return cube

def zero_poles(cube):
    # Polar values should have no longitude dependence
    # For aerosol emissions they should be zero
    latdim = cube.coord_dims('latitude')
    assert latdim == (1,)
    cube.data[:,0] = 0.
    cube.data[:,-1] = 0.

# Change the calendar to Gregorian for the model
def set_gregorian(var):
    time = var.coord('time')
    origin = time.units.origin
    newunits = cf_units.Unit(origin, calendar='proleptic_gregorian')

    tvals = np.array(time.points)
    tbnds = np.array(time.bounds)
    for i in range(len(time.points)):
        date = time.units.num2date(tvals[i])
        newdate = cftime.DatetimeProlepticGregorian(date.year, date.month, date.day, date.hour, date.minute, date.second)
        tvals[i] = newunits.date2num(newdate)
        for j in range(2):
            date = time.units.num2date(tbnds[i][j])
            newdate = cftime.DatetimeProlepticGregorian(date.year, date.month, date.day, date.hour, date.minute, date.second)
            tbnds[i][j] = newunits.date2num(newdate)
    time.points = tvals
    time.bounds = tbnds
    time.units = newunits

def set_coord_system(cube):
    cube.coord('latitude').coord_system = iris.coord_systems.GeogCS(6371229.0)
    cube.coord('longitude').coord_system = iris.coord_systems.GeogCS(6371229.0)

def save_ancil(cubes, filename):
    # Single year creates file with correct time_type=2
    # ants creates files with the model_version header set to the ants version. UM vn7.3
    # interprets 201 as an old unsupported dump format.
    # Need to reset to 703
    ants.__version__ = '7.3'
    # Handle both a list and a single cube
    if not type(cubes) is list:
        cubes = [cubes]
    for cube in cubes:
        cube.attributes["grid_staggering"] = 3 # New dynamics
        cube.attributes["time_type"] = 1 # Gregorian
        set_gregorian(cube)
    # ants doesn't set the calendar header for monthly fields
    # See fileformats/ancil/time_headers.py
    # UM vn7.3 doesn't handle the missing value, so set the value with mule
    # mule doesn't work in place on a file, so inital save to a temporary
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = os.path.join(tmp, 'ancil')
        save.ancil(cubes, tmp_path)
        ff = mule.AncilFile.from_file(tmp_path)
        ff.fixed_length_header.calendar = 1
        ff.to_file(filename)

def fix_coords(cube):
    cube.coord('latitude').coord_system = mask_esm15.coord('latitude').coord_system
    cube.coord('longitude').coord_system = mask_esm15.coord('longitude').coord_system
