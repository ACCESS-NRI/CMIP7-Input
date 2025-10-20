from argparse import ArgumentParser

import iris
import numpy as np
from cmip7_ancil_argparse import common_parser
from cmip7_ancil_constants import REAL_MISSING_DATA_INDICATOR
from cmip7_HI import (
    CMIP7_HI_BEG_YEAR,
    CMIP7_HI_END_YEAR,
    esm_hi_forcing_save_dirpath,
)
from solar.cmip7_solar import cmip7_solar_dirpath, load_cmip7_solar_cube

SOLAR_ARRAY_BEG_YEAR = 1700
SOLAR_ARRAY_END_YEAR = 2300


def parse_args():
    parser = ArgumentParser(
        prog="cmip7_HI_solar_generate",
        description=(
            "Generate input files from CMIP7 historical solar forcings"
        ),
        parents=[
            common_parser(),
        ],
    )
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_hi_solar_year_mean(cube):
    """
    Calculate mean TSI values for each year and save them into an array.
    """
    NBR_YEARS = SOLAR_ARRAY_END_YEAR - SOLAR_ARRAY_BEG_YEAR + 1
    solar_array = np.zeros(NBR_YEARS)
    tsi_sum = 0.0
    # Calculate and save the mean annual TSI
    # for each CMI7 historical year.
    for year in range(CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR + 1):
        year_cons = iris.Constraint(time=lambda cell: cell.point.year == year)
        year_cube = cube.extract(year_cons)
        year_mean = year_cube.collapsed("time", iris.analysis.MEAN).data
        solar_array[year - SOLAR_ARRAY_BEG_YEAR] = year_mean
        tsi_sum += year_mean
    # Calculate the mean TSI over the CMIP7 historical years.
    NBR_CMIP7_HI_YEARS = CMIP7_HI_END_YEAR - CMIP7_HI_BEG_YEAR
    tsi_mean = tsi_sum / NBR_CMIP7_HI_YEARS

    # For the years from SOLAR_ARRAY_BEG_YEAR to CMIP7_HI_BEG_YEAR - 1,
    # set the saved TSI value to the mean TSI.
    for year in range(SOLAR_ARRAY_BEG_YEAR, CMIP7_HI_BEG_YEAR):
        solar_array[year - SOLAR_ARRAY_BEG_YEAR] = tsi_mean

    # For the years from CMIP7_HI_END_YEAR + 1 to SOLAR_ARRAY_END_YEAR,
    # set the saved TSI value to the real missing data indicator
    for year in range(CMIP7_HI_END_YEAR + 1, SOLAR_ARRAY_END_YEAR + 1):
        solar_array[year - SOLAR_ARRAY_BEG_YEAR] = REAL_MISSING_DATA_INDICATOR
    return solar_array


def cmip7_hi_solar_save(args, cube):
    """
    Save the TSI values for each year into a text file.
    """
    solar_array = cmip7_hi_solar_year_mean(cube)
    save_dirpath = esm_hi_forcing_save_dirpath(args)
    # Ensure that the save directory exists.
    save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
    save_filepath = save_dirpath / args.save_filename
    with open(save_filepath, "w") as save_file:
        for year in range(SOLAR_ARRAY_BEG_YEAR, SOLAR_ARRAY_END_YEAR + 1):
            year_mean = solar_array[year - SOLAR_ARRAY_BEG_YEAR]
            if year_mean == REAL_MISSING_DATA_INDICATOR:
                print(year, f"{year_mean:.1f}", file=save_file)
            else:
                print(year, f"{year_mean:.3f}", file=save_file)


if __name__ == "__main__":
    args = parse_args()

    cmip7_filename = (
        "multiple_input4MIPs_solar_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}.nc"
    )
    cmip7_filepath = cmip7_solar_dirpath(args, "mon") / cmip7_filename

    solar_irradiance_cube = load_cmip7_solar_cube(cmip7_filepath)

    cmip7_hi_solar_save(args, solar_irradiance_cube)
