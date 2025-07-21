import ants
import ants.io
import ants.io.save as save
import cftime
import cf_units
import iris
import mule
import numpy as np
import os
import tempfile

from pathlib import Path

from cmip7_ancil_constants import UM_VERSION
from cmip7_ancil_paths import ESM16_GRID_MASK_FILE


esm_grid_mask = iris.load_cube(ESM16_GRID_MASK_FILE)
esm_grid_mask.coord('latitude').guess_bounds()
esm_grid_mask.coord('longitude').guess_bounds()

interpolation_scheme = iris.analysis.AreaWeighted(mdtol=0.5)


def join_pathname(path_prefix, path_suffix):
    return str(Path(path_prefix) / path_suffix)


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


def fix_coords(cube):
    cube.coord('latitude').coord_system = (
        esm_grid_mask.coord('latitude').coord_system)
    cube.coord('longitude').coord_system = (
        esm_grid_mask.coord('longitude').coord_system)


def zero_poles(cube):
    # Polar values should have no longitude dependence
    # For aerosol emissions they should be zero
    latdim = cube.coord_dims('latitude')
    assert latdim == (1,)
    cube.data[:, 0] = 0.
    cube.data[:, -1] = 0.


def save_ancil(cubes, ancil_dirname, ancil_filename):
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
    with tempfile.TemporaryDirectory() as temp:
        ancil_tempname = join_pathname(temp, ancil_filename)
        save.ancil(cubes, ancil_tempname)
        sm = mule.STASHmaster.from_version(UM_VERSION)
        ff = mule.AncilFile.from_file(ancil_tempname, stashmaster=sm)
        ff.fixed_length_header.calendar = 1
        # Ensure that the directory exists.
        os.makedirs(ancil_dirname, mode=0o755, exist_ok=True)
        ancil_pathname = join_pathname(ancil_dirname, ancil_filename)
        ff.to_file(ancil_pathname)
