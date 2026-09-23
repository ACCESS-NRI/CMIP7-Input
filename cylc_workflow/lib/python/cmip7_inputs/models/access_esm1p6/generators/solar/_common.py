"""Shared helpers for ACCESS-ESM1.6 solar generators."""

from __future__ import annotations

from pathlib import Path

import iris
import numpy as np

from iris.coord_categorisation import add_year 

from cmip7_inputs.models.access_esm1p6.generators._constants import (
    REAL_MISSING_DATA_INDICATOR,
    PI_START_YEAR,
    HI_START_YEAR,
    HI_END_YEAR,
)

def load_solar_cube(path):
    '''
    Loads the solar irradiance cube from an ancil file
    '''
    name_constraint = iris.Constraint(name="solar_irradiance")
    return iris.load_cube(path, name_constraint)

def compute_solar_yearly_mean(cube, start_year, end_year):
    """
    Calculate mean Total Solar Irradiance (TSI) values for each year and save them into an array.
    The TSI is the solar power per unit area received at the top of the Earth's atmosphere.
    """

    # Extract year range from the cube
    period = cube.extract(
        iris.Constraint(time=lambda cell: start_year <= cell.point.year <= end_year)
    )
    add_year(period, "time")
    # Calculate yearly mean
    yearly_means = period.aggregated_by("year", iris.analysis.MEAN)

    # Get array  
    solar_array = yearly_means.data.copy()  
    # Substitute NaNs with REAL_MISSING_DATA_INDICATOR  
    solar_array[np.isnan(solar_array)] = REAL_MISSING_DATA_INDICATOR

    return solar_array

def save_solar(save_filepath, cube, start_year, end_year):
    """
    Save the TSI values for each year into a text file, in the format:  
    <year1> <value1>  
    <year2> <value2>  
    <year3> <value3>.
    """
    solar_array = compute_solar_yearly_mean(cube, start_year, end_year)

    years = np.arange(HI_START_YEAR, HI_END_YEAR + 1)
    is_missing = solar_array == REAL_MISSING_DATA_INDICATOR

    # Missing-data entries get 1 decimal place, real values get 3.
    lines = [
        f"{year} {value:.3f}" if not missing else f"{year} {value:.1f}"
        for year, value, missing in zip(years, solar_array, is_missing)
    ]

    # Ensure that the save directory exists and write the file atomically.
    save_filepath.parent.mkdir(parents=True, exist_ok=True)
    save_filepath.write_text("\n".join(lines) + "\n")
