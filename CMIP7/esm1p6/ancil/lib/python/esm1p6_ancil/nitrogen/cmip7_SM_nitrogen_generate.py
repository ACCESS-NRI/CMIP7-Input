'''
This script generates the CMIP7 ScenarioMIP nitrogen ancillary file.
It loads the CMIP7 ScenarioMIP nitrogen data, regrids it to match the ESM1.5 mask, and saves the result as an ancillary file.
The script uses the argparse module to parse command line arguments, including the paths to the input and output files, and the grid information. 
'''
from argparse import ArgumentParser
from pathlib import Path

from cmip7_ancil_argparse import common_parser
from cmip7_ancil_common import extend_years
from cmip7_ancil_constants import ANCIL_TODAY
from nitrogen.cmip7_nitrogen import (
    cmip7_nitrogen_dirpath,
    load_cmip7_nitrogen,
    regrid_cmip7_nitrogen,
    save_cmip7_nitrogen,
)


def parse_args():
    '''
    Parse the command line arguments for CMIP7 ScenarioMIP nitrogen ancil file generation.
    '''
    parser = ArgumentParser(
        parents=[common_parser()],
        prog="cmip7_SM_nitrogen_generate",
        description=(
            "Generate input files from CMIP7 ScenarioMIP nitrogen forcings"
        ),
    )
    parser.add_argument("--scenario")
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()

# TODO: Is this function really needed? There are other functions that do the same thing, but with different names. Maybe we can unify them.
# Like cmip7_pi_nitrogen_filepath
def cmip7_sm_nitrogen_filepath(args, species):
    '''
    Return the file path to the CMIP7 ScenarioMIP nitrogen dataset for the given species.
    '''
    dirpath = cmip7_nitrogen_dirpath(args, "ScenarioMIP", "mon", species)
    filename = (
        f"{species}_input4MIPs_surfaceFluxes_ScenarioMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}.nc"
    )
    return dirpath / filename


def esm_sm_nitrogen_save_dirpath(args):
    '''
    Return the directory path to save the ESM1.5 ScenarioMIP nitrogen ancil file.
    '''
    return (
        Path(args.ancil_target_dirname)
        / "scenarios"
        / args.scenario
        / "atmosphere"
        / "land"
        / "biogeochemistry"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


if __name__ == "__main__":
    '''
    Generate the CMIP7 ScenarioMIP nitrogen ancillary file.
    '''
    args = parse_args()

    # Load the CMIP7 datasets
    nitrogen_cube = load_cmip7_nitrogen(args, cmip7_sm_nitrogen_filepath)
    # Regrid to match the ESM1.5 mask and extend the time series
    esm_cube = extend_years(regrid_cmip7_nitrogen(args, nitrogen_cube))
    # Save the ancillary
    save_cmip7_nitrogen(args, esm_cube, esm_sm_nitrogen_save_dirpath)
