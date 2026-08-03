'''
This script modifies the CMIP7 ScenarioMIP greenhouse gas namelist based on the provided command line arguments.
It loads the CMIP7 ScenarioMIP greenhouse gas series for each greenhouse gas, and then updates the namelist file with the loaded data.
'''
# TODO: Is this script exaclty the same as cmip7_HI_ghg_generate.py? 
# If so, we can merge them into one script and just pass the scenario as an argument. 

from argparse import ArgumentParser

from cmip7_ancil_argparse import dataset_parser, path_parser
from cmip7_SM import (
    CMIP7_SM_BEG_YEAR,
    CMIP7_SM_END_YEAR,
)
from ghg.cmip7_ghg import GHG_MOLAR_MASS
from ghg.cmip7_ghg_series import (
    cmip7_ghg_update_namelists_file,
    load_cmip7_ghg_series_mmr,
)


def parse_args():
    '''
    Parse the command line arguments for CMIP7 ScenarioMIP greenhouse gas namelist modification.
    '''
    parser = ArgumentParser(
        parents=[path_parser(), dataset_parser()],
        prog="cmip7_SM_ghg_generate",
        description=(
            # TODO: This description might not be accurate. The script modifies the namelist, it does not generate input files.
            "Generate input files from CMIP7 ScenarioMIP "
            "greenhouse gas forcings"
        ),
    )
    parser.add_argument("--dataset-date-range")
    return parser.parse_args()


if __name__ == "__main__":
    '''
    Modify the CMIP7 ScenarioMIP greenhouse gas namelist.
    '''
    args = parse_args()

    CMIP7_SM_GHG_BEG_YEAR = CMIP7_SM_BEG_YEAR
    ghg_mmr_dict = dict()
    for ghg in GHG_MOLAR_MASS:
        ghg_mmr_dict[ghg] = load_cmip7_ghg_series_mmr(
            args, "ScenarioMIP", ghg, CMIP7_SM_GHG_BEG_YEAR, CMIP7_SM_END_YEAR
        )

    # Patch the greenhouse gas namelist.
    cmip7_ghg_update_namelists_file(
        ghg_mmr_dict, CMIP7_SM_GHG_BEG_YEAR, CMIP7_SM_END_YEAR
    )
