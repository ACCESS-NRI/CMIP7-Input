from __future__ import annotations
from argparse import Namespace

from cmip7_inputs.core.context import GenerationRequest

from os import fsdecode
from pathlib import Path
import iris
import mule
import ants
import ants.io.save as save
import cftime
import cf_units
import numpy as np
import tempfile

from cmip7_inputs.models.access_esm1p6.generators._constants import (
    UM_VERSION,
    MONTHS_IN_A_YEAR
)

INTERPOLATION_SCHEME = iris.analysis.AreaWeighted(mdtol=0.5)


def cmip7_parse_args(request: GenerationRequest) -> Namespace:
    '''
    Parse the command line arguments for CMIP7 historical
    solar ancil file generation.
    '''
    return Namespace(**request.options)

def esm_grid_mask_filepath(args):
    '''Return the file path to the ESM1.5 grid mask file.'''
    return (
        Path(args.esm15_inputs_dirname)
        / "modern"
        / "share"
        / "atmosphere"
        / "grids"
        / args.esm_grid_rel_dirname
        / args.esm15_grid_version
        / "qrparm.mask"
    )

def esm_grid_mask_cube(args):
    '''Load the ESM1.5 grid mask cube from the specified file path.'''
    cube = iris.load_cube(esm_grid_mask_filepath(args))
    # Estimate bounds from the coordinate values. It is a convenience method for filling in missing bounds.
    cube.coord("latitude").guess_bounds()
    cube.coord("longitude").guess_bounds()
    return cube

def fix_coords(args, cube):
    '''
    Fix the coordinates of the cube to be compatible with the ESM1.5 grid.
    '''
    # Load grid mask cube to get the coordinate system
    esm_grid_mask = esm_grid_mask_cube(args)
    # Make the target cube use the same coordinate system as the reference cube
    cube.coord("latitude").coord_system = esm_grid_mask.coord(
        "latitude"
    ).coord_system
    cube.coord("longitude").coord_system = esm_grid_mask.coord(
        "longitude"
    ).coord_system

def set_gregorian(var, replace_bounds=False):
    '''
    Change the calendar of the time coordinate of the given iris cube to Gregorian.
    If replace_bounds is True, the time bounds will be replaced with the first day of the month and the first day of the next month. 
    If False, the bounds will be converted to Gregorian.
    '''
    # Change the calendar to Gregorian for the model
    time = var.coord("time")
    origin = time.units.origin
    newunits = cf_units.Unit(origin, calendar="proleptic_gregorian")

    tvals = np.array(time.points)
    tbnds = np.array(time.bounds)
    # Convert each time point to Gregorian and update the time points and bounds
    for i in range(len(time.points)):
        date = time.units.num2date(tvals[i])
        newdate = cftime.DatetimeProlepticGregorian(
            date.year, date.month, date.day, date.hour, date.minute, date.second
        )
        tvals[i] = newunits.date2num(newdate)
        # If replacing bounds, set the bounds to the first day of the month and the first day of the next month
        if replace_bounds:
            beg_date = cftime.DatetimeProlepticGregorian(
                date.year,
                date.month,
                1,
                date.hour,
                date.minute,
                date.second,
            )
            tbnds[i][0] = newunits.date2num(beg_date)
            if date.month == 12:
                end_year = date.year + 1
                end_month = 1
            else:
                end_year = date.year
                end_month = date.month + 1
            end_date = cftime.DatetimeProlepticGregorian(
                end_year,
                end_month,
                1,
                date.hour,
                date.minute,
                date.second,
            )
            tbnds[i][1] = newunits.date2num(end_date)
        # If not replacing bounds, convert the existing bounds to Gregorian
        else:
            for j in range(2):
                date = time.units.num2date(tbnds[i][j])
                newdate = cftime.DatetimeProlepticGregorian(
                    date.year,
                    date.month,
                    date.day,
                    date.hour,
                    date.minute,
                    date.second,
                )
                tbnds[i][j] = newunits.date2num(newdate)
    time.points = tvals
    time.bounds = tbnds
    time.units = newunits

def save_ancil(
    cubes, save_dirpath, save_filename, gregorian=True, replace_bounds=False
):
    """
    Handle both a list and a single cube
    """
    if not isinstance(cubes, list):
        cubes = [cubes]
    """
    Set correct cube grid and time attributes
    Single year creates file with correct time_type=2
    """
    for cube in cubes:
        cube.attributes["grid_staggering"] = 3  # New dynamics
        if gregorian:
            cube.attributes["time_type"] = 1  # Gregorian
            set_gregorian(cube, replace_bounds=replace_bounds)
    """
    ANTS doesn't set the calendar header for monthly fields
    See fileformats/ancil/time_headers.py
    UM vn7.3 doesn't handle the missing value, so set the value with mule
    Mule doesn't work in place on a file, so inital save to a temporary
    ANTS creates files with the model_version header set to the ants version.
    UM vn7.3 interprets 201 as an old unsupported dump format.
    Need to reset to 703.
    """
    ants.__version__ = UM_VERSION
    with tempfile.TemporaryDirectory() as temp_dirname:
        save_temp_pathname = fsdecode(Path(temp_dirname) / save_filename)
        save.ancil(cubes, save_temp_pathname)
        sm = mule.STASHmaster.from_version(UM_VERSION)
        ff = mule.AncilFile.from_file(save_temp_pathname, stashmaster=sm)
        ff.fixed_length_header.calendar = 1
        # Ensure that the directory exists.
        save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
        save_file_pathname = fsdecode(save_dirpath / save_filename)
        ff.to_file(save_file_pathname)

def extend_years(cube):
    """
    Extend a cube representing a monthly time series by duplicating
    and adjusting the first and last years.
    Based on Crown copyright code from ozone_cmip6_ancillary_for_suite.py
    by Steven Hardiman of the UK Met Office.
    """
    time_coord = cube.coord("time")
    time_points = time_coord.points
    # Do not extend a cube containing less than two years of data.
    if len(time_points) < MONTHS_IN_A_YEAR * 2:
        return cube

    # Duplicate the first year.
    length_one_year = time_points[MONTHS_IN_A_YEAR] - time_points[0]
    beg_year = cube[:MONTHS_IN_A_YEAR].copy()
    beg_year_tc = beg_year.coord("time")
    beg_year_tc.points = beg_year_tc.points - length_one_year
    if time_coord.has_bounds():
        beg_year_tc.bounds = beg_year_tc.bounds - length_one_year

    # Duplicate the last year.
    length_one_year = time_points[-1] - time_points[-1 - MONTHS_IN_A_YEAR]
    end_year = cube[-MONTHS_IN_A_YEAR:].copy()
    end_year_tc = end_year.coord("time")
    end_year_tc.points = end_year_tc.points + length_one_year
    if time_coord.has_bounds():
        end_year_tc.bounds = end_year_tc.bounds + length_one_year

    # Return a cube with extended years.
    cubelist = iris.cube.CubeList((beg_year, cube, end_year))
    return cubelist.concatenate_cube()