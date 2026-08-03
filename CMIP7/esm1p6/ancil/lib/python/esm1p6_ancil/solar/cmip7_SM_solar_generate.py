'''
CMIP7 ScenarioMIP solar ancil file generation script.
The script takes command line arguments for the dataset version, dataset date range, and save filename.
The generated file is saved in the specified directory path.
The script uses the cmip7_solar module to load the solar irradiance data and calculate the average TSI values for each year.
'''

from argparse import ArgumentParser

from cmip7_ancil_argparse import common_parser
from cmip7_SM import esm_sm_forcing_save_dirpath
from solar.cmip7_solar import (
    cmip7_solar_dirpath,
    cmip7_solar_save,
    load_cmip7_solar_cube,
)

CMIP7_SM_SOLAR_BEG_YEAR = 2022
CMIP7_SM_SOLAR_END_YEAR = 2299


def parse_args():
    '''
    Parse the command line arguments for CMIP7 ScenarioMIP solar ancil file generation.
    '''
    parser = ArgumentParser(
        prog="cmip7_SM_solar_generate",
        description=(
            "Generate input files from CMIP7 ScenarioMIP solar forcings"
        ),
        parents=[
            common_parser(),
        ],
    )
    # TODO: These are common arguments to other ancil generation scripts.
    parser.add_argument("--scenario")
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_sm_solar_save(args, cube):
    """
    Save the TSI values for each year into a text file.
    """
    save_dirpath = esm_sm_forcing_save_dirpath(args)
    cmip7_solar_save(
        args,
        cube,
        CMIP7_SM_SOLAR_BEG_YEAR,
        CMIP7_SM_SOLAR_END_YEAR,
        save_dirpath,
    )


if __name__ == "__main__":
    '''
    Generate the CMIP7 ScenarioMIP solar ancillary file.
    '''
    args = parse_args()

    dirpath = cmip7_solar_dirpath(args, "ScenarioMIP", "mon")
    filename = (
        "multiple_input4MIPs_solar_ScenarioMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}.nc"
    )
    dataset_path = dirpath / filename

    solar_irradiance_cube = load_cmip7_solar_cube(dataset_path)

    cmip7_sm_solar_save(args, solar_irradiance_cube)
