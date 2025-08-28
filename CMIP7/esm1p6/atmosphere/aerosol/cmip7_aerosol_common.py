import iris
from iris.util import equalise_attributes, unify_time_units


def load_cmip7_aerosol(args, filepath_fn, species, date_range, constraint):
    filepath = filepath_fn(args, species, date_range)
    cube = iris.load_cube(filepath, constraint)
    return cube


def load_cmip7_aerosol_list(
    args, filepath_list_fn, species, date_range_list, constraint
):
    filepath_list = filepath_list_fn(args, species, date_range_list)
    cube_list = iris.load_raw(filepath_list, constraint)
    equalise_attributes(cube_list)
    unify_time_units(cube_list)
    cube = cube_list.concatenate_cube()
    return cube


def zero_poles(cube):
    # Polar values should have no longitude dependence
    # For aerosol emissions they should be zero
    latdim = cube.coord_dims('latitude')
    assert latdim == (1,)
    cube.data[:, 0] = 0.0
    cube.data[:, -1] = 0.0
