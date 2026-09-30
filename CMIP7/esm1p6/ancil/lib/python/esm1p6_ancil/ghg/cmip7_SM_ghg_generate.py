from argparse import ArgumentParser

from cmip7_ancil_argparse import dataset_parser, ext_parser, path_parser
from cmip7_SM import (
    CMIP7_SM_BEG_YEAR,
    CMIP7_SM_END_YEAR,
    CMIP7_SM_EXT_END_YEAR,
)
from ghg.cmip7_ghg import GHG_MOLAR_MASS
from ghg.cmip7_ghg_series import (
    cmip7_ghg_update_namelists_file,
    load_cmip7_ghg_series_mmr,
)


def parse_args():
    parser = ArgumentParser(
        parents=[path_parser(), dataset_parser(), ext_parser()],
        prog="cmip7_SM_ghg_generate",
        description=(
            "Generate input files from CMIP7 ScenarioMIP "
            "greenhouse gas forcings"
        ),
    )
    parser.add_argument("--dataset-date-range")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    target_end_year = (
        (args.end_year or CMIP7_SM_EXT_END_YEAR)
        if args.ext
        else CMIP7_SM_END_YEAR
    )

    ghg_mmr_dict = dict()
    for ghg in GHG_MOLAR_MASS:
        series = load_cmip7_ghg_series_mmr(
            args,
            "ScenarioMIP",
            ghg,
            CMIP7_SM_BEG_YEAR,
            target_end_year,
            ext=args.ext,
        )
        ghg_mmr_dict[ghg] = series

    # Patch the greenhouse gas namelist.
    cmip7_ghg_update_namelists_file(
        ghg_mmr_dict, CMIP7_SM_BEG_YEAR, target_end_year
    )
