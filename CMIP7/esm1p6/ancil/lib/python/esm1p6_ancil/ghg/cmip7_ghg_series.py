'''
    Load the CMIP7 greenhouse gas series and update the namelist file.
    This module provides functions to load the CMIP7 greenhouse gas series for each greenhouse gas, and then update the namelist file with the loaded data.
'''

from collections import OrderedDict
from pathlib import Path

import cftime
import f90nml
import iris
import iris.cube
import iris.util
import numpy as np
from ghg.cmip7_ghg import (
    cmip7_ghg_dirpath,
    cmip7_ghg_filename,
    cmip7_ghg_mmr,
    cmip7_pro_greg_date_constraint_from_years,
)


def load_cmip7_ghg_series_mmr(args, activity, ghg, beg_year, end_year):
    '''
    Load the CMIP7 greenhouse gas mass mixing ratio for the given greenhouse gas, between the specified years.
    '''
    dirpath = cmip7_ghg_dirpath(args, activity, ghg)
    filename = cmip7_ghg_filename(args, activity, ghg)
    cmip7_filepath = dirpath / filename

    # Read in the CMIP7 cube.
    full_cube = iris.load_cube(cmip7_filepath)

    # Check that we have the right greenhouse gas.
    variable_id = full_cube.metadata.attributes["variable_id"]
    assert ghg == variable_id
    new_cube = full_cube.copy()
    # Linearly interpolate to Jan 1 so that UM time interpolation
    # reproduces annual means
    new_cube.data[:-1] = 0.5 * (full_cube.data[:-1] + full_cube.data[1:])
    # Extrapolate the last year
    new_cube.data[-1] = full_cube.data[-1] + 0.5 * (
        full_cube.data[-1] - full_cube.data[-2]
    )
    full_cube_time = full_cube.coord("time")
    units = full_cube_time.units
    new_cube_time = new_cube.coord("time")
    full_cube_beg_year = units.num2date(full_cube_time.points[0]).year
    # Can't assign to elements of time.points so create a temporary array
    tvals = np.array(new_cube_time.points)
    for i in range(len(tvals)):
        date = units.num2date(full_cube_time.points[i])
        # Interpolated data is Jan 1 of the next year
        newdate = cftime.DatetimeProlepticGregorian(
            date.year + 1, 1, 1, 0, 0, 0
        )
        tvals[i] = units.date2num(newdate)
    new_cube_time.points = tvals
    if full_cube_beg_year == beg_year:
        print(
            f"The first year in the forcing file is {beg_year}. "
            f"Extrapolate backwards."
        )
        beg_year_cube = full_cube[0:1].copy()
        # Extrapolate the first year
        beg_year_cube.data[0] = full_cube.data[0] + 0.5 * (
            full_cube.data[0] - full_cube.data[1]
        )
        # Exrapolated data is Jan 1 of the first year
        beg_year_cube_time = beg_year_cube.coord("time")
        beg_tvals = np.array(beg_year_cube_time.points)
        new_beg_date = cftime.DatetimeProlepticGregorian(
            beg_year, 1, 1, 0, 0, 0
        )
        beg_tvals[0] = units.date2num(new_beg_date)
        beg_year_cube_time.points = beg_tvals
        # Try dropping time bounds
        beg_year_cube_time.bounds = None
        new_cube_time.bounds = None
        new_cube_list = iris.cube.CubeList([beg_year_cube, new_cube])
        iris.util.unify_time_units(new_cube_list)
        iris.util.equalise_attributes(new_cube_list)
        new_cube = new_cube_list.concatenate_cube()

    # Extract the series years.
    date_constraint = cmip7_pro_greg_date_constraint_from_years(
        beg_year, end_year
    )
    series_cube = new_cube.extract(date_constraint)

    # Determine the mass mixing ratio.
    ghg_mmr_list = []
    for year in range(beg_year, end_year + 1):
        year_constraint = cmip7_pro_greg_date_constraint_from_years(year, year)
        year_cube = series_cube.extract(year_constraint)
        print(year, year_cube.data)
        ghg_mmr_list.append(cmip7_ghg_mmr(year_cube, ghg))
    return ghg_mmr_list


def read_namelists_lines_up_to(namelists_filepath, exclude_group):
    """
    Read lines from namelists_filepath up to but not including a line that
    contains the string exclude_group. This function is used to avoid having
    to use f90nml to reformat an entire namelist file. Versions of f90nml
    older than v1.5 contain a bug that affects null values in namelists.
    See https://github.com/marshallward/f90nml/pull/180
    """
    if not namelists_filepath.exists():
        raise FileNotFoundError(
            f"Namelist file {namelists_filepath} does not exist"
        )
    # Read the namelists_filepath file up to but not including
    # the namelist group given by exclude_group.
    namelists = []
    exclude_str = "&" + exclude_group.lower()
    with open(namelists_filepath) as namelists_file:
        for line in namelists_file:
            if exclude_str in line.lower():
                break
            namelists.append(line)
    return "".join(namelists)


def format_namelist(namelist, float_format="13.6e"):
    """
    Change the namelist formatting to the preferred format.
    """
    namelist.float_format = float_format
    namelist.end_comma = True
    namelist.false_repr = ".FALSE."
    namelist.true_repr = ".TRUE."
    namelist.uppercase = True


def cmip7_ghg_namelist_str(ghg_mmr_dict, ghg_namelist_name, beg_year, end_year):
    """
    Use the greenhouse gas mass mixing ratios to
    produce a replacement clmchfcg namelist as a string.
    """
    # Map each greenhouse gas to an index in the
    # historical climate forcing arrays.
    GHG_NAMELIST_INDEX = {
        "cfc11": 3,
        "cfc12": 4,
        "cfc113": 7,
        "ch4": 1,
        "co2": 0,
        "hcfc22": 8,
        "hfc125": 9,
        "hfc134a": 10,
        "n2o": 2,
    }
    GHG_NAMELIST_NBR_SPECIES = 11
    OLD_REAL_MISSING_DATA_VALUE = -32768.0

    # Create arrays to populate the namelist group.
    NBR_YEARS = end_year - beg_year + 1
    namelist_nyears_shape = (GHG_NAMELIST_NBR_SPECIES,)
    namelist_nyears = np.full(namelist_nyears_shape, NBR_YEARS)
    namelist_years_shape = (GHG_NAMELIST_NBR_SPECIES, NBR_YEARS)
    namelist_years = np.broadcast_to(
        np.array(range(beg_year, end_year + 1)),
        namelist_years_shape,
    ).T
    namelist_levls = np.zeros(namelist_years.shape)
    for ghg in GHG_NAMELIST_INDEX:
        ghg_index = GHG_NAMELIST_INDEX[ghg]
        namelist_levls[:, ghg_index] = ghg_mmr_dict[ghg]
    namelist_rates = np.full(namelist_years.shape, OLD_REAL_MISSING_DATA_VALUE)

    # Create a dictionary to use to patch the namelist group.
    namelist_dict = {
        "l_clmchfcg": True,
        "clim_fcg_nyears": namelist_nyears,
        "clim_fcg_years": namelist_years,
        "clim_fcg_levls": namelist_levls,
        "clim_fcg_rates": namelist_rates,
    }

    patch = {ghg_namelist_name: OrderedDict(namelist_dict)}
    patch_namelist = f90nml.namelist.Namelist(patch)

    # Change the namelist arrays to row major.
    patch_str = str(patch_namelist)
    parser = f90nml.Parser()
    parser.row_major = True
    row_major_patch_namelist = parser.reads(patch_str)
    # Correctly format the namelist.
    format_namelist(row_major_patch_namelist)
    # The format is ignored unless you print the namelist or
    # convert it to a string.
    return str(row_major_patch_namelist)


def cmip7_ghg_update_namelists_file(ghg_mmr_dict, beg_year, end_year):
    """
    Use the greenhouse gas mass mixing ratios in ghg_mmr_dict
    to replace the greenhouse gas namelist in the relevant namelists file.
    """
    namelists_filepath = Path("atmosphere") / "namelists"
    ghg_namelist_name = "clmchfcg"
    # Read the original namelists file up to ghg_namelist_name.
    namelists_str = read_namelists_lines_up_to(
        namelists_filepath, ghg_namelist_name
    )
    # Use ghg_mmr_dict and ghg_namelist_name to create
    # a replacement namelist as a string.
    ghg_namelist_str = cmip7_ghg_namelist_str(
        ghg_mmr_dict, ghg_namelist_name, beg_year, end_year
    )
    # Replace the original namelists file.
    with open(namelists_filepath, "w") as namelists_file:
        print(namelists_str + ghg_namelist_str, file=namelists_file)
