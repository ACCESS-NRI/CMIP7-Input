import iris
from iris.util import equalise_attributes, unify_time_units


def load_cmip7_aerosol(args, filepath_fn, species, date_range, constraint):
    """Load an aerosol emissions Iris cube for a specific species and date
    range.

    Args:
        args (argparse.Namespace): Command-line arguments containing dataset
            configuration.
        filepath_fn (callable): Function taking (args, species, date_range) and
            returning pathlib.Path.
        species (str): Aerosol species identifier (e.g. 'BC', 'OC', 'SO2').
        date_range (str): Date range string (e.g. '185001-185012').
        constraint (iris.Constraint or None): Constraint on variables or
            coordinates to load.

    Returns:
        iris.cube.Cube: Loaded Iris cube.
    """
    filepath = filepath_fn(args, species, date_range)
    cube = iris.load_cube(filepath, constraint)
    return cube


def cmip7_aerosol_filepath_list(args, filepath_fn, species, date_range_list):
    """Generate a list of netCDF file paths across multiple date range chunks.

    Args:
        args (argparse.Namespace): Command-line arguments.
        filepath_fn (callable): Function returning a pathlib.Path given (args,
            species, date_range).
        species (str): Aerosol species name.
        date_range_list (list of str): List of date range string chunks.

    Returns:
        list of pathlib.Path: Resolved file paths.
    """
    return [
        filepath_fn(args, species, date_range) for date_range in date_range_list
    ]


def load_cmip7_aerosol_list(
    args, filepath_fn, species, date_range_list, constraint
):
    """Load, equalize attributes, unify time units, and concatenate aerosol
    cubes across multiple files.

    Args:
        args (argparse.Namespace): Command-line arguments.
        filepath_fn (callable): Callback to resolve file paths.
        species (str): Aerosol species name.
        date_range_list (list of str): List of date ranges to concatenate.
        constraint (iris.Constraint or None): Constraint applied during
            loading.

    Returns:
        iris.cube.Cube: Concatenated continuous Iris cube spanning the full
            date range.
    """
    filepath_list = cmip7_aerosol_filepath_list(
        args, filepath_fn, species, date_range_list
    )
    cube_list = iris.load_raw(filepath_list, constraint)
    equalise_attributes(cube_list)
    unify_time_units(cube_list)
    cube = cube_list.concatenate_cube()
    return cube


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
