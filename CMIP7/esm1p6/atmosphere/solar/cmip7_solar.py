from pathlib import Path

import iris
import numpy as np
from cmip7_ancil_constants import REAL_MISSING_DATA_INDICATOR
from cmip7_PI import CMIP7_PI_YEAR

SOLAR_ARRAY_BEG_YEAR = 1700
SOLAR_ARRAY_END_YEAR = 2300
SOLAR_PI_DEFAULT_YEAR_MEAN = 1361.603


def cmip7_solar_dirpath(args, activity, period):
    return (
        Path(args.cmip7_source_data_dirname)
        / activity
        / "SOLARIS-HEPPA"
        / args.dataset_version
        / "atmos"
        / period
        / "multiple"
        / "gn"
        / args.dataset_vdate
    )


def load_cmip7_solar_cube(path):
    cubelist = iris.load(path)
    name_constraint = iris.Constraint(name="solar_irradiance")
    return cubelist.extract_cube(name_constraint)


def cmip7_solar_year_mean(
    cube, beg_year, end_year, array_beg_year, array_end_year
):
    """
    Calculate mean TSI values for each year and save them into an array.
    """
    NBR_YEARS = array_end_year - array_beg_year + 1
    solar_array = np.zeros(NBR_YEARS)
    # Calculate and save the mean annual TSI for each CMIP7 historical year.
    year_range = range(beg_year, end_year + 1)
    pi_year_mean = SOLAR_PI_DEFAULT_YEAR_MEAN
    for year in year_range:
        year_cons = iris.Constraint(time=lambda cell: cell.point.year == year)
        year_cube = cube.extract(year_cons)
        year_mean = year_cube.collapsed("time", iris.analysis.MEAN).data
        solar_array[year - array_beg_year] = year_mean
        # Save the year mean for the pre-industrial year.
        if year == CMIP7_PI_YEAR:
            pi_year_mean = year_mean

    # For the years from array_beg_year to beg_year - 1,
    # set the saved TSI value to the pre-industrial year mean TSI.
    for year in range(array_beg_year, beg_year):
        solar_array[year - array_beg_year] = pi_year_mean

    # For the years from end_year + 1 to array_end_year,
    # set the saved TSI value to the real missing data indicator
    for year in range(end_year + 1, array_end_year + 1):
        solar_array[year - array_beg_year] = REAL_MISSING_DATA_INDICATOR
    return solar_array


def cmip7_solar_save(
    args,
    cube,
    beg_year,
    end_year,
    save_dirpath,
    array_beg_year=SOLAR_ARRAY_BEG_YEAR,
    array_end_year=SOLAR_ARRAY_END_YEAR,
):
    """
    Save the TSI values for each year into a text file.
    """
    solar_array = cmip7_solar_year_mean(
        cube, beg_year, end_year, array_beg_year, array_end_year
    )
    # Ensure that the save directory exists.
    save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
    save_filepath = save_dirpath / args.save_filename
    with open(save_filepath, "w") as save_file:
        for year in range(array_beg_year, array_end_year + 1):
            year_mean = solar_array[year - array_beg_year]
            if year_mean == REAL_MISSING_DATA_INDICATOR:
                print(year, f"{year_mean:.1f}", file=save_file)
            else:
                print(year, f"{year_mean:.3f}", file=save_file)
