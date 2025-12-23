# Interpolate CMIP7 EH CO2 emissions to ESM1.6 grid
from pathlib import Path

from aerosol.cmip7_aerosol_anthro import cmip7_aerosol_anthro_interpolate
from aerosol.cmip7_HI_aerosol_anthro import (
    load_cmip7_hi_aerosol_anthro,
    parse_args,
)
from cmip7_ancil_constants import ANCIL_TODAY

SPECIES = "CO2"
STASH_ITEM = 251


def esm_eh_co2_save_dirpath(args):
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "historical-emissions"
        / "atmosphere"
        / "forcing"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


def cmip7_eh_co2_anthro_interpolate(args):
    cmip7_aerosol_anthro_interpolate(
        args,
        load_cmip7_hi_aerosol_anthro,
        SPECIES,
        STASH_ITEM,
        esm_eh_co2_save_dirpath(args),
    )


if __name__ == "__main__":
    args = parse_args(species=SPECIES)

    cmip7_eh_co2_anthro_interpolate(args)
