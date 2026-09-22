import warnings
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

    is_ext = getattr(args, "ext", False)
    target_end_year = (
        (getattr(args, "end_year", None) or CMIP7_SM_EXT_END_YEAR)
        if is_ext
        else CMIP7_SM_END_YEAR
    )

    ghg_mmr_dict = dict()
    try:
        effective_end_year = target_end_year
        for ghg in GHG_MOLAR_MASS:
            series = load_cmip7_ghg_series_mmr(
                args, "ScenarioMIP", ghg, CMIP7_SM_BEG_YEAR, target_end_year
            )
            ghg_mmr_dict[ghg] = series
            loaded_end_year = CMIP7_SM_BEG_YEAR + len(series) - 1
            if loaded_end_year < effective_end_year:
                effective_end_year = loaded_end_year

        # If any series fell back, synchronize all series to effective_end_year
        expected_len = effective_end_year - CMIP7_SM_BEG_YEAR + 1
        for ghg in GHG_MOLAR_MASS:
            if len(ghg_mmr_dict[ghg]) > expected_len:
                ghg_mmr_dict[ghg] = ghg_mmr_dict[ghg][:expected_len]

        # Patch the greenhouse gas namelist.
        cmip7_ghg_update_namelists_file(
            ghg_mmr_dict, CMIP7_SM_BEG_YEAR, effective_end_year
        )

    except Exception as e:
        warnings.warn(f"Could not update GHG namelist: {e}", UserWarning)
