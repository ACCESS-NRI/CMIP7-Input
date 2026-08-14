"""Shared helpers for ACCESS-ESM1.6 solar generators."""

"""Contains the functions originally in cmip7_solar.py"""

from __future__ import annotations

from pathlib import Path

import iris
import numpy as np

from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.models.access_esm1p6.generators._common_PI import CMIP7_PI_YEAR
from cmip7_inputs.models.access_esm1p6.generators._constants import REAL_MISSING_DATA_INDICATOR


SOLAR_ARRAY_BEG_YEAR = 1700
SOLAR_ARRAY_END_YEAR = 2300
SOLAR_PI_DEFAULT_YEAR_MEAN = 1361.603

def cmip7_solar_dirpath(request: GenerationRequest, activity, period)->Path:
    '''
    Return the directory path for the CMIP7 SOLARIS-HEPPA solar ancil file.
    '''
    return (
        Path(request.options['cmip7-source-data-dirname'])
        / activity
        / "SOLARIS-HEPPA"
        / request.options['dataset-version']
        / "atmos"
        / period
        / "multiple"
        / "gn"
        / request.options['dataset-vdate']
    )

def load_cmip7_solar_cube(path):
    '''
    Loads the solar irradiance cube from the CMIP7 SOLARIS-HEPPA solar ancil file.
    '''
    """cubelist = iris.load(path)
    name_constraint = iris.Constraint(name="solar_irradiance")
    return cubelist.extract_cube(name_constraint)"""
    return path

def cmip7_solar_year_mean(cube, beg_year, end_year):
    """
    Calculate mean TSI values for each year and save them into an array.
    TSI stands for Total Solar Irradiance, which is the solar power per unit area received at the top of the Earth's atmosphere.
    """
    NBR_YEARS = SOLAR_ARRAY_END_YEAR - SOLAR_ARRAY_BEG_YEAR + 1
    solar_array = np.zeros(NBR_YEARS)
    # Calculate and save the mean annual TSI for each CMIP7 historical year.
    year_range = range(beg_year, end_year + 1)
    pi_year_mean = SOLAR_PI_DEFAULT_YEAR_MEAN
    for year in year_range:
        year_cons = iris.Constraint(time=lambda cell: cell.point.year == year)
        # Extract the cube for the year
        year_cube = cube.extract(year_cons)
        # Calculate year mean 
        year_mean = year_cube.collapsed("time", iris.analysis.MEAN).data
        solar_array[year - SOLAR_ARRAY_BEG_YEAR] = year_mean
        # Save the year mean for the pre-industrial year.
        if year == CMIP7_PI_YEAR:
            pi_year_mean = year_mean

    # For the years from SOLAR_ARRAY_BEG_YEAR to beg_year - 1, i.e. before beg_year,
    # set the saved TSI value to the pre-industrial year mean TSI.
    for year in range(SOLAR_ARRAY_BEG_YEAR, beg_year):
        solar_array[year - SOLAR_ARRAY_BEG_YEAR] = pi_year_mean

    # For the years from CMIP7_HI_END_YEAR + 1 to SOLAR_ARRAY_END_YEAR, i.e. after end_year,
    # set the saved TSI value to the real missing data indicator
    for year in range(end_year + 1, SOLAR_ARRAY_END_YEAR + 1):
        solar_array[year - SOLAR_ARRAY_BEG_YEAR] = REAL_MISSING_DATA_INDICATOR
    return solar_array

def cmip7_solar_save(request: GenerationRequest, cube, beg_year, end_year, save_dirpath):
    """
    Save the TSI values for each year into a text file.
    """
    solar_array = cmip7_solar_year_mean(cube, beg_year, end_year)
    # Ensure that the save directory exists.
    save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
    save_filepath = save_dirpath / request.options['save-filename']
    with open(save_filepath, "w") as save_file:
        for year in range(SOLAR_ARRAY_BEG_YEAR, SOLAR_ARRAY_END_YEAR + 1):
            year_mean = solar_array[year - SOLAR_ARRAY_BEG_YEAR]
            if year_mean == REAL_MISSING_DATA_INDICATOR:
                print(year, f"{year_mean:.1f}", file=save_file)
            else:
                print(year, f"{year_mean:.3f}", file=save_file)


def write_mock_solar_file(request: GenerationRequest, dirpath: Path = None, dataset_path: Path = None) -> Path:
    """Write a placeholder file describing the request.

    Shared by every ACCESS-ESM1.6 solar generator until real solar
    forcing processing is implemented.
    """
    request.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = request.output_dir / (
        f"{request.model}_{request.experiment}_{request.input_name}.txt"
    )
    output_path.write_text(
        "Mock CMIP7 input file\n"
        f"model: {request.model}\n"
        f"experiment: {request.experiment}\n"
        f"input_name: {request.input_name}\n"
        f"options: {request.options}\n"

        # Historical solar forcing options
        f"dataset-version: {request.options['dataset-version']}\n"
        f"dataset-vdate: {request.options['dataset-vdate']}\n"
        f"dataset-date-range: {request.options['dataset-date-range']}\n"
        f"save-filename: {request.options['save-filename']}\n"
        

        f"cmip7-source-data-dirname: {request.options['cmip7-source-data-dirname']}\n"
        f"ancil_target_dirname: {request.options['ancil_target_dirname']}\n"

        "Dirpath function test:\n"
        f"dirpath: {dirpath}\n"
        f"dataset_path: {dataset_path}\n"
        # ScenarioMIP
        #f"scenario: {request.options['scenario']}\n"
        
    )
    return output_path
