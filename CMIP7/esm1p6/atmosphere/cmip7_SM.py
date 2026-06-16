from pathlib import Path

from cmip7_ancil_constants import ANCIL_TODAY

CMIP7_SM_BEG_YEAR = 2022
CMIP7_SM_END_YEAR = 2100


def esm_sm_forcing_save_dirpath(args):
    return (
        Path(args.ancil_target_dirname)
        / "scenarios"
        / args.scenario
        / "atmosphere"
        / "forcing"
        / "resolution_independent"
        / ANCIL_TODAY
    )
