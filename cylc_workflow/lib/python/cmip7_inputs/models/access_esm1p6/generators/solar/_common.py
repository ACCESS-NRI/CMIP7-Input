"""Shared helpers for ACCESS-ESM1.6 solar generators."""

from __future__ import annotations

from pathlib import Path

import iris
import numpy as np

from iris.coord_categorisation import add_year 

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
    Loads the solar irradiance cube from an ancil file
    '''
    name_constraint = iris.Constraint(name="solar_irradiance")
    return iris.load_single(path, name_constraint)

def compute_solar_yearly_mean(cube, start_year, end_year):
    """
    Calculate mean Total Solar Irradiance (TSI) values for each year and save them into an array.
    The TSI is the solar power per unit area received at the top of the Earth's atmosphere.
    """
    n_years = SOLAR_ARRAY_END_YEAR - SOLAR_ARRAY_START_YEAR + 1
    solar_array = np.full(n_years, REAL_MISSING_DATA_INDICATOR, dtype=float)

    # Compute all yearly means in one pass instead of looping extract+collapse per year.
    period = cube.extract(
        iris.Constraint(time=lambda cell: start_year <= cell.point.year <= end_year)
    )
    add_year(period, "time")
    yearly_means = period.aggregated_by("year", iris.analysis.MEAN)

    years = yearly_means.coord("year").points
    means = yearly_means.data

    idx = years - SOLAR_ARRAY_START_YEAR
    solar_array[idx] = means

    # Years before start_year: fill with the pre-industrial year mean (fall back to default).
    pi_matches = means[years == PI_START_YEAR]
    pi_year_mean = pi_matches[0] if pi_matches.size else SOLAR_PI_DEFAULT_YEARLY_MEAN
    solar_array[: start_year - SOLAR_ARRAY_START_YEAR] = pi_year_mean

    # Years after end_year already default to REAL_MISSING_DATA_INDICATOR from np.full.
    return solar_array

def save_solar(args, cube, beg_year, end_year, save_dirpath):
    """
    Save the TSI values for each year into a text file.
    """
    solar_array = compute_solar_yearly_mean(cube, beg_year, end_year)

    years = np.arange(SOLAR_ARRAY_START_YEAR, SOLAR_ARRAY_END_YEAR + 1)
    is_missing = solar_array == REAL_MISSING_DATA_INDICATOR

    # Missing-data entries get 1 decimal place, real values get 3.
    lines = [
        f"{year} {value:.1f}" if missing else f"{year} {value:.3f}"
        for year, value, missing in zip(years, solar_array, is_missing)
    ]

    # Ensure that the save directory exists and write the file atomically.
    save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
    save_filepath = save_dirpath / args.save_filename
    save_filepath.write_text("\n".join(lines) + "\n")
