"""Shared helpers for ACCESS-ESM1.6 solar generators."""

from __future__ import annotations

from pathlib import Path

import iris
import numpy as np

from iris.coord_categorisation import add_year 

from cmip7_inputs.models.access_esm1p6.generators._constants import (
    REAL_MISSING_DATA_INDICATOR,
    HI_START_YEAR,
    HI_END_YEAR
)

def load_solar_cube(path):
    '''
    Loads the solar irradiance cube from an ancil file
    '''
    name_constraint = iris.Constraint(name="solar_irradiance")
    return iris.load_cube(path, name_constraint)

def compute_solar_yearly_mean(cube):
    """
    Calculate mean Total Solar Irradiance (TSI) values for each year and save them into an array.
    The TSI is the solar power per unit area received at the top of the Earth's atmosphere.
    """
    n_years = HI_END_YEAR - HI_START_YEAR + 1
    solar_array = np.full(n_years, REAL_MISSING_DATA_INDICATOR, dtype=float)

    # Compute all yearly means in one pass instead of looping extract+collapse per year.
    period = cube.extract(
        iris.Constraint(time=lambda cell: HI_START_YEAR <= cell.point.year <= HI_END_YEAR)
    )
    add_year(period, "time")
    yearly_means = period.aggregated_by("year", iris.analysis.MEAN)

    years = yearly_means.coord("year").points
    means = yearly_means.data

    idx = years - HI_START_YEAR
    solar_array[idx] = means

    return solar_array

def save_solar(cube, save_dirpath, save_filename):
    """
    Save the TSI values for each year into a text file.
    """
    solar_array = compute_solar_yearly_mean(cube)

    years = np.arange(HI_START_YEAR, HI_END_YEAR + 1)
    is_missing = solar_array == REAL_MISSING_DATA_INDICATOR

    # Missing-data entries get 1 decimal place, real values get 3.
    lines = [
        f"{year} {value:.1f}" if missing else f"{year} {value:.3f}"
        for year, value, missing in zip(years, solar_array, is_missing)
    ]

    # Ensure that the save directory exists and write the file atomically.
    save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
    save_filepath = save_dirpath / save_filename
    save_filepath.write_text("\n".join(lines) + "\n")
