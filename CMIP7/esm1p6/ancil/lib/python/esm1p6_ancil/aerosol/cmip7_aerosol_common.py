'''
CMIP7 aerosol emissions data common functions
'''
import iris
from iris.util import equalise_attributes, unify_time_units


def load_cmip7_aerosol(args, filepath_fn, species, date_range, constraint):
    '''
    Load the CMIP7 aerosol emissions data for the given species and date range, and apply the given constraint.
    '''
    filepath = filepath_fn(args, species, date_range)
    cube = iris.load_cube(filepath, constraint)
    return cube


def cmip7_aerosol_filepath_list(args, filepath_fn, species, date_range_list):
    '''
    Return a list of file paths to the CMIP7 aerosol emissions data for the given species and list of date ranges.
    '''
    return [
        filepath_fn(args, species, date_range) for date_range in date_range_list
    ]


def load_cmip7_aerosol_list(
    args, filepath_fn, species, date_range_list, constraint
):
    '''
    Load the CMIP7 aerosol emissions data for the given species and list of date ranges, and apply the given constraint.
    '''
    filepath_list = cmip7_aerosol_filepath_list(
        args, filepath_fn, species, date_range_list
    )
    cube_list = iris.load_raw(filepath_list, constraint)
    # Remove all attributes that differ between cubes
    equalise_attributes(cube_list)
    # Unify the time units of all cubes to a common unit
    unify_time_units(cube_list)
    cube = cube_list.concatenate_cube()
    return cube

# TODO: Maybe it should be moved to cmip7_ancil_common.py, since it is not specific to aerosol data.
def zero_poles(cube):
    # Polar values should have no longitude dependence
    # For aerosol emissions they should be zero
    latdim = cube.coord_dims("latitude")
    assert latdim == (1,)
    data = cube.data.copy()
    data[:, 0] = 0.0
    data[:, -1] = 0.0
    cube.data = data
