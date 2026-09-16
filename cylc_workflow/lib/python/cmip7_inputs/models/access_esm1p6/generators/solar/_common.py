"""Shared helpers for ACCESS-ESM1.6 solar generators."""

from __future__ import annotations

from pathlib import Path

import iris
import numpy as np

from cmip7_inputs.models.access_esm1p6.generators._constants import (
    REAL_MISSING_DATA_INDICATOR,
    PI_START_YEAR,
    SOLAR_ARRAY_START_YEAR,
    SOLAR_ARRAY_END_YEAR,
    SOLAR_PI_DEFAULT_YEARLY_MEAN
)


def get_solar_dirpath(args, activity, period)->Path:
    '''
    Return the directory path for the CMIP7 SOLARIS-HEPPA solar ancil file.
    '''
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

def load_solar_cube(path):
    '''
    Loads the solar irradiance cube from the CMIP7 SOLARIS-HEPPA solar ancil file.
    '''
    cubelist = iris.load(path)
    name_constraint = iris.Constraint(name="solar_irradiance")
    return cubelist.extract_cube(name_constraint)

def compute_solar_yearly_mean(cube, beg_year, end_year):
    """
    Calculate mean Total Solar Irradiance (TSI) values for each year and save them into an array.
    The TSI is the solar power per unit area received at the top of the Earth's atmosphere.
    """
    NBR_YEARS = SOLAR_ARRAY_END_YEAR - SOLAR_ARRAY_START_YEAR + 1
    solar_array = np.zeros(NBR_YEARS)
    # Calculate and save the mean annual TSI for each CMIP7 historical year.
    year_range = range(beg_year, end_year + 1)
    pi_year_mean = SOLAR_PI_DEFAULT_YEARLY_MEAN
    for year in year_range:
        year_cons = iris.Constraint(time=lambda cell: cell.point.year == year)
        # Extract the cube for the year
        year_cube = cube.extract(year_cons)
        # Calculate year mean 
        year_mean = year_cube.collapsed("time", iris.analysis.MEAN).data
        solar_array[year - SOLAR_ARRAY_START_YEAR] = year_mean
        # Save the year mean for the pre-industrial year.
        if year == PI_START_YEAR:
            pi_year_mean = year_mean

    # For the years from SOLAR_ARRAY_START_YEAR to beg_year - 1, i.e. before beg_year,
    # set the saved TSI value to the pre-industrial year mean TSI.
    for year in range(SOLAR_ARRAY_START_YEAR, beg_year):
        solar_array[year - SOLAR_ARRAY_START_YEAR] = pi_year_mean

    # For the years from CMIP7_HI_END_YEAR + 1 to SOLAR_ARRAY_END_YEAR, i.e. after end_year,
    # set the saved TSI value to the real missing data indicator
    for year in range(end_year + 1, SOLAR_ARRAY_END_YEAR + 1):
        solar_array[year - SOLAR_ARRAY_START_YEAR] = REAL_MISSING_DATA_INDICATOR
    return solar_array

def save_solar(args, cube, beg_year, end_year, save_dirpath):
    """
    Save the TSI values for each year into a text file.
    """
    solar_array = compute_solar_yearly_mean(cube, beg_year, end_year)
    # Ensure that the save directory exists.
    save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
    save_filepath = save_dirpath / args.save_filename
    with open(save_filepath, "w") as save_file:
        for year in range(SOLAR_ARRAY_START_YEAR, SOLAR_ARRAY_END_YEAR + 1):
            year_mean = solar_array[year - SOLAR_ARRAY_START_YEAR]
            if year_mean == REAL_MISSING_DATA_INDICATOR:
                print(year, f"{year_mean:.1f}", file=save_file)
            else:
                print(year, f"{year_mean:.3f}", file=save_file)
