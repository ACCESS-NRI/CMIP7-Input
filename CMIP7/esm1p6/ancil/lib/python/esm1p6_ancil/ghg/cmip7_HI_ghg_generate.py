'''
This script modifies the CMIP7 historical greenhouse gas namelist based on the provided command line arguments. 
It loads the CMIP7 historical greenhouse gas series for each greenhouse gas, and then updates the namelist file with the loaded data.
'''
from argparse import ArgumentParser

from cmip7_ancil_argparse import dataset_parser, path_parser
from cmip7_HI import (
    CMIP7_HI_BEG_YEAR,
    CMIP7_HI_END_YEAR,
)
from ghg.cmip7_ghg import GHG_MOLAR_MASS
from ghg.cmip7_ghg_series import (
    cmip7_ghg_update_namelists_file,
    load_cmip7_ghg_series_mmr,
)


def parse_args():
    '''
    Parse the command line arguments for CMIP7 historical greenhouse gas namelist modification.
    '''
    parser = ArgumentParser(
        parents=[path_parser(), dataset_parser()],
        prog="cmip7_HI_ghg_generate",
        description=(
            # TODO: This description might not be accurate. The script modifies the namelist, it does not generate input files.
            "Generate input files from CMIP7 historical greenhouse gas forcings"
        ),
    )
    parser.add_argument("--dataset-date-range")
    return parser.parse_args()


if __name__ == "__main__":
    '''
    Modify the CMIP7 historical greenhouse gas namelist.
    '''
    args = parse_args()

    ghg_mmr_dict = dict()
    for ghg in GHG_MOLAR_MASS:
        ghg_mmr_dict[ghg] = load_cmip7_ghg_series_mmr(
            args, "CMIP", ghg, CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR
        )

    # Patch the greenhouse gas namelist.
    cmip7_ghg_update_namelists_file(
        ghg_mmr_dict, CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR
    )
