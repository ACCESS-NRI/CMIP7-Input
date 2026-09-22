# Interpolate CMIP7 ES CO2 emissions to ESM1.6 grid
import warnings
from argparse import ArgumentParser
from pathlib import Path

import iris
from aerosol.cmip7_aerosol_common import zero_poles
from aerosol.cmip7_SM_aerosol_anthro import (
    check_aerosol_ext_available,
    load_cmip7_sm_aerosol_air_anthro,
    load_cmip7_sm_aerosol_anthro,
)
from cmip7_ancil_argparse import common_parser, ext_parser
from cmip7_ancil_common import (
    INTERPOLATION_SCHEME,
    esm_grid_mask_cube,
    save_ancil,
)
from cmip7_ancil_constants import ANCIL_TODAY
from cmip7_SM import CMIP7_SM_END_YEAR

SPECIES = "CO2"
STASH_ITEM = 251


def parse_args():
    parser = ArgumentParser(
        prog=f"cmip7_ES_{SPECIES}_interpolate",
        description=(
            f"Generate input files from CMIP7 ScenarioMIP {SPECIES} forcings"
        ),
        parents=[common_parser(), ext_parser()],
    )
    parser.add_argument("--dataset-air-version")
    parser.add_argument("--dataset-air-vdate")
    parser.add_argument("--scenario")
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def esm_es_co2_save_dirpath(args):
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / f"esm-scen7-{args.scenario}"
        / "atmosphere"
        / "forcing"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


def cmip7_es_co2_anthro_interpolate(args):
    if getattr(args, "ext", False):
        surf_avail = check_aerosol_ext_available(args, SPECIES, is_air=False)
        air_avail = check_aerosol_ext_available(args, SPECIES, is_air=True)
        if not (surf_avail and air_avail):
            warnings.warn(
                f"CO2 extension dataset(s) incomplete "
                f"(surface: {surf_avail}, air: {air_avail}). "
                f"Falling back to baseline {CMIP7_SM_END_YEAR}.",
                UserWarning,
            )
            args.ext = False

    cube = load_cmip7_sm_aerosol_anthro(args, SPECIES, collapse_sector=True)
    cube_air = load_cmip7_sm_aerosol_air_anthro(args, SPECIES)
    cube_tot = cube + cube_air

    esm_cube = cube_tot.regrid(esm_grid_mask_cube(args), INTERPOLATION_SCHEME)
    esm_cube.data = esm_cube.data.filled(0.0)
    zero_poles(esm_cube)
    esm_cube.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=STASH_ITEM
    )

    save_dirpath = esm_es_co2_save_dirpath(args)
    save_ancil(esm_cube, save_dirpath, args.save_filename)


if __name__ == "__main__":
    args = parse_args()

    cmip7_es_co2_anthro_interpolate(args)
