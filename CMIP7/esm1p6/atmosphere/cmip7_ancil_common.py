import tempfile
from os import fsdecode
from pathlib import Path

import ants
import ants.io
import ants.io.save as save
import cf_units
import cftime
import iris
import mule
import numpy as np
from cmip7_ancil_constants import UM_VERSION

INTERPOLATION_SCHEME = iris.analysis.AreaWeighted(mdtol=0.5)


def cmip7_date_constraint_from_years(beg_year, end_year):
    # For CMIP6 and CMIP7 data
    beg_date = cftime.DatetimeNoLeap(beg_year, 1, 1)
    end_date = cftime.DatetimeNoLeap(end_year, 12, 31)
    return iris.Constraint(time=lambda cell: beg_date <= cell.point <= end_date)


def cmip7_date_constraint_from_args(args):
    return cmip7_date_constraint_from_years(
        args.constraint_beg_year, args.constraint_end_year
    )


def esm_grid_mask_filepath(args):
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
    cube = iris.load_cube(esm_grid_mask_filepath(args))
    cube.coord("latitude").guess_bounds()
    cube.coord("longitude").guess_bounds()
    return cube


def set_gregorian(var):
    # Change the calendar to Gregorian for the model
    time = var.coord("time")
    origin = time.units.origin
    newunits = cf_units.Unit(origin, calendar="proleptic_gregorian")

    tvals = np.array(time.points)
    tbnds = np.array(time.bounds)
    for i in range(len(time.points)):
        date = time.units.num2date(tvals[i])
        newdate = cftime.DatetimeProlepticGregorian(
            date.year, date.month, date.day, date.hour, date.minute, date.second
        )
        tvals[i] = newunits.date2num(newdate)
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


def set_coord_system(cube):
    coord_system = iris.coord_systems.GeogCS(6371229.0)
    cube.coord("latitude").coord_system = coord_system
    cube.coord("longitude").coord_system = coord_system


def fix_coords(args, cube):
    esm_grid_mask = esm_grid_mask_cube(args)
    cube.coord("latitude").coord_system = esm_grid_mask.coord(
        "latitude"
    ).coord_system
    cube.coord("longitude").coord_system = esm_grid_mask.coord(
        "longitude"
    ).coord_system


def zero_poles(cube):
    # Polar values should have no longitude dependence
    # For aerosol emissions they should be zero
    latdim = cube.coord_dims("latitude")
    assert latdim == (1,)
    cube.data[:, 0] = 0.0
    cube.data[:, -1] = 0.0


def save_ancil(cubes, save_dirpath, save_filename):
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
        cube.attributes["time_type"] = 1  # Gregorian
        set_gregorian(cube)
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
