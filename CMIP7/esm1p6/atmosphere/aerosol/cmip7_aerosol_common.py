import numpy as np
import ants
import ants.io
import ants.io.save as save
import mule
import iris
import cftime
import cf_units
import os
import tempfile

from pathlib import Path

from cmip7_ancil_constants import (
        CMIP7_PI_YEAR,
        UM_VERSION)
from cmip7_ancil_paths import (
        ANCIL_TARGET_PATH,
        ESM16_GRID_MASK_FILE)

CMIP7_AEROSOL_SAVE_DIR = Path(ANCIL_TARGET_PATH) / 'esm16_aerosols'
# Ensure that the directory exists.
os.makedirs(CMIP7_AEROSOL_SAVE_DIR, mode=0o755, exist_ok=True)


def cmip7_aerosol_save_path(filename):
    return str(Path(CMIP7_AEROSOL_SAVE_DIR) / filename)


mask_esm15 = iris.load_cube(ESM16_GRID_MASK_FILE)
mask_esm15.coord('latitude').guess_bounds()
mask_esm15.coord('longitude').guess_bounds()

interpolation_scheme = iris.analysis.AreaWeighted(mdtol=0.5)

# For CMIP6 and CMIP7 data
CMIP7_PI_BEG_DATE = cftime.DatetimeNoLeap(CMIP7_PI_YEAR, 1, 1)
CMIP7_PI_END_DATE = cftime.DatetimeNoLeap(CMIP7_PI_YEAR, 12, 31)
CMIP7_PI_DATE_CONSTRAINT = iris.Constraint(
        time=lambda cell: CMIP7_PI_BEG_DATE <= cell.point < CMIP7_PI_END_DATE)


def zero_poles(cube):
    # Polar values should have no longitude dependence
    # For aerosol emissions they should be zero
    latdim = cube.coord_dims('latitude')
    assert latdim == (1,)
    cube.data[:, 0] = 0.
    cube.data[:, -1] = 0.


def set_gregorian(var):
    # Change the calendar to Gregorian for the model
    time = var.coord('time')
    origin = time.units.origin
    newunits = cf_units.Unit(origin, calendar='proleptic_gregorian')

    tvals = np.array(time.points)
    tbnds = np.array(time.bounds)
    for i in range(len(time.points)):
        date = time.units.num2date(tvals[i])
        newdate = cftime.DatetimeProlepticGregorian(
            date.year,
            date.month,
            date.day,
            date.hour,
            date.minute,
            date.second)
        tvals[i] = newunits.date2num(newdate)
        for j in range(2):
            date = time.units.num2date(tbnds[i][j])
            newdate = cftime.DatetimeProlepticGregorian(
                date.year,
                date.month,
                date.day,
                date.hour,
                date.minute,
                date.second)
            tbnds[i][j] = newunits.date2num(newdate)
    time.points = tvals
    time.bounds = tbnds
    time.units = newunits


def set_coord_system(cube):
    coord_system = iris.coord_systems.GeogCS(6371229.0)
    cube.coord('latitude').coord_system = coord_system
    cube.coord('longitude').coord_system = coord_system


def save_ancil(cubes, filename):
    """
    Single year creates file with correct time_type=2
    ants creates files with the model_version header set to the ants version.
    UM vn7.3 interprets 201 as an old unsupported dump format.
    Need to reset to 703.
    """
    ants.__version__ = UM_VERSION
    # Handle both a list and a single cube
    if not type(cubes) is list:
        cubes = [cubes]
    for cube in cubes:
        cube.attributes["grid_staggering"] = 3  # New dynamics
        cube.attributes["time_type"] = 1  # Gregorian
        set_gregorian(cube)
    # ants doesn't set the calendar header for monthly fields
    # See fileformats/ancil/time_headers.py
    # UM vn7.3 doesn't handle the missing value, so set the value with mule
    # mule doesn't work in place on a file, so inital save to a temporary
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = os.path.join(tmp, 'ancil')
        save.ancil(cubes, tmp_path)
        sm = mule.STASHmaster.from_version(UM_VERSION)
        ff = mule.AncilFile.from_file(tmp_path, stashmaster=sm)
        ff.fixed_length_header.calendar = 1
        ff.to_file(filename)


def fix_coords(cube):
    cube.coord('latitude').coord_system = (
        mask_esm15.coord('latitude').coord_system)
    cube.coord('longitude').coord_system = (
        mask_esm15.coord('longitude').coord_system)
