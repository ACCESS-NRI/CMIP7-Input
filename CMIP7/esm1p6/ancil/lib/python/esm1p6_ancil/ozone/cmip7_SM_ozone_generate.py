import warnings
from argparse import ArgumentParser
from pathlib import Path

from cmip7_ancil_argparse import (
    ext_parser,
    grid_parser,
    path_parser,
)
from cmip7_ancil_common import save_ancil, tile_constant_years
from cmip7_ancil_constants import ANCIL_TODAY
from cmip7_SM import CMIP7_SM_END_YEAR, CMIP7_SM_EXT_END_YEAR
from ozone.cmip7_ozone import (
    fix_cmip7_ozone,
    load_cmip7_ozone,
    ozone_parser,
)


def parse_args():
    parser = ArgumentParser(
        parents=[path_parser(), grid_parser(), ozone_parser(), ext_parser()],
        prog="cmip7_SM_ozone_generate",
        description=(
            "Generate input files from UK CMIP7 ScenarioMIP ozone forcings"
        ),
    )
    parser.add_argument("--scenario")
    return parser.parse_args()


def esm_sm_ozone_save_dirpath(args):
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / f"scen7-{args.scenario}"
        / "atmosphere"
        / "forcing"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


def save_cmip7_sm_ozone(args, cube):
    # Save as an ancillary file
    save_dirpath = esm_sm_ozone_save_dirpath(args)
    save_ancil(cube, save_dirpath, args.save_filename, replace_bounds=True)


if __name__ == "__main__":
    args = parse_args()

    # Load the CMIP7 datasets
    try:
        ozone_cube = load_cmip7_ozone(args)
    except Exception as e:
        warnings.warn(f"Could not load ozone dataset: {e}", UserWarning)
        ozone_cube = None

    if ozone_cube is not None:
        # Match the ESM1.5 mask
        esm_cube = fix_cmip7_ozone(args, ozone_cube)
        if getattr(args, "ext", False):
            target_end_year = (
                getattr(args, "end_year", None) or CMIP7_SM_EXT_END_YEAR
            )
            # Ozone input from UKESM contains 1 padding year at each boundary
            # (e.g. 2021 and 2101). When extending to target_end_year (2150),
            # tile to target_end_year + 1 (2151) to preserve UM end padding.
            esm_cube = tile_constant_years(
                esm_cube, CMIP7_SM_END_YEAR, target_end_year + 1
            )
        # Save the ancillary
        save_cmip7_sm_ozone(args, esm_cube)
