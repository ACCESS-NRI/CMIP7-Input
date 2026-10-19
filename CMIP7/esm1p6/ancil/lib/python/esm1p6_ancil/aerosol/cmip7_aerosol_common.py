import os

import iris
import netCDF4
from iris.util import equalise_attributes, unify_time_units


def load_cmip7_aerosol(dataset, constraint):
    """Load an aerosol emissions Iris cube from a single dataset.

    Args:
        dataset (os.PathLike): Dataset (or path) of the netCDF file to load.
        constraint (iris.Constraint or None): Constraint on variables or
            coordinates to load.

    Returns:
        iris.cube.Cube: Loaded Iris cube.
    """
    return iris.load_cube(os.fspath(dataset), constraint)


def load_cmip7_aerosol_list(datasets, constraint):
    """Load, equalize attributes, unify time units, and concatenate aerosol
    cubes across multiple files.

    Args:
        datasets (iterable of os.PathLike): Ordered datasets (or paths) of
            the netCDF files to concatenate.
        constraint (iris.Constraint or None): Constraint applied during
            loading.

    Returns:
        iris.cube.Cube: Concatenated continuous Iris cube spanning the full
            date range.
    """
    filepath_list = [os.fspath(dataset) for dataset in datasets]
    cube_list = iris.load_raw(filepath_list, constraint)
    equalise_attributes(cube_list)
    unify_time_units(cube_list)
    cube = cube_list.concatenate_cube()
    return cube


def load_sector_dict(dataset):
    """Parse the netCDF sector attribute to map sector names to indices.

    Uses netCDF4 to extract the sector string attribute ('id: name; ...')
    since Iris does not parse sector coordinates by default.

    Args:
        dataset (os.PathLike): Dataset (or path) of a netCDF file with a
            sector coordinate.

    Returns:
        dict: Mapping of sector name (e.g. 'Energy', 'Industrial') to
            integer index.
    """
    sectord = dict()
    with netCDF4.Dataset(os.fspath(dataset)) as d:
        for s in d["sector"].ids.split(";"):
            i, name = s.split(":")
            sectord[name.strip()] = int(i)
    return sectord


def zero_poles(cube):
    """Zero the polar latitude rows of an aerosol emissions cube in place.

    Aerosol emissions should have no longitude dependence and evaluate to zero
    at the poles.
    Modifies latitude indices 0 and -1.

    Args:
        cube (iris.cube.Cube): Cube with latitude dimension at index 1.
    """
    # Polar values should have no longitude dependence
    # For aerosol emissions they should be zero
    latdim = cube.coord_dims("latitude")
    assert latdim == (1,)
    # cube.data can be read-only, so we copy it here
    data = cube.data.copy()
    data[:, 0] = 0.0
    data[:, -1] = 0.0
    cube.data = data
