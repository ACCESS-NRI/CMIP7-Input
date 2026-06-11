from pathlib import Path

from cmip7_ancil_constants import ANCIL_TODAY
from cmip7_SM import CMIP7_SM_BEG_YEAR, CMIP7_SM_END_YEAR

CMIP7_SM_AEROSOL_BEG_YEAR = CMIP7_SM_BEG_YEAR - 1
CMIP7_SM_AEROSOL_END_YEAR = CMIP7_SM_END_YEAR + 1


def esm_sm_aerosol_ancil_dirpath(args):
    return (
        Path(args.ancil_target_dirname)
        / "scenarios"
        / args.scenario
        / "atmosphere"
        / "aerosol"
    )


def esm_sm_aerosol_save_dirpath(args):
    return (
        esm_sm_aerosol_ancil_dirpath(args)
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )
