from pathlib import Path

from ..cmip7_ancil_constants import ANCIL_TODAY
from ..cmip7_HI import CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR

CMIP7_HI_AEROSOL_BEG_YEAR = CMIP7_HI_BEG_YEAR - 1
CMIP7_HI_AEROSOL_END_YEAR = CMIP7_HI_END_YEAR


def esm_hi_aerosol_ancil_dirpath(ancil_root_dirname):
    return (
        Path(ancil_root_dirname)
        / "modern"
        / "historical"
        / "atmosphere"
        / "aerosol"
    )


def esm_hi_aerosol_save_dirpath(args):
    return (
        esm_hi_aerosol_ancil_dirpath(args.ancil_target_dirname)
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )
