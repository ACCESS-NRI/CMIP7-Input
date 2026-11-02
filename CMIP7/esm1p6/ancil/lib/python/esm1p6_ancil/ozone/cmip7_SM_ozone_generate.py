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
    """Parse command-line arguments for ScenarioMIP ozone ancillary generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, grid, ozone
            dataset, extension, and scenario options.
    """
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
    """Construct the destination directory path for ScenarioMIP ozone ancillary
    files.

    Args:
        args (argparse.Namespace): Command-line arguments containing output
            path configuration (ancil_target_dirname, scenario,
            esm_grid_rel_dirname).

    Returns:
        pathlib.Path: Target directory path under
            modern/scen7-{scenario}/atmosphere/forcing/.
    """
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
    """Write the processed ScenarioMIP ozone cube to an ancillary file with
    replaced bounds.

    Args:
        args (argparse.Namespace): Command-line arguments containing output
            path and filename.
        cube (iris.cube.Cube): Harmonized (and optionally extended) ozone cube
            to save.
    """
    # Save as an ancillary file
    save_dirpath = esm_sm_ozone_save_dirpath(args)
    save_ancil(cube, save_dirpath, args.save_filename, replace_bounds=True)


if __name__ == "__main__":
    args = parse_args()

    # Load the CMIP7 datasets
    ozone_cube = load_cmip7_ozone(args)

    # Match the ESM1.5 mask
    esm_cube = fix_cmip7_ozone(args, ozone_cube)
    if args.ext:
        target_end_year = args.end_year or CMIP7_SM_EXT_END_YEAR
        # Ozone input from UKESM contains 1 padding year at each boundary
        # (e.g. 2021 and 2101). When extending to target_end_year (2150),
        # tile to target_end_year + 1 (2151) to preserve UM end padding.
        esm_cube = tile_constant_years(
            esm_cube, CMIP7_SM_END_YEAR, target_end_year + 1
        )
    # Save the ancillary
    save_cmip7_sm_ozone(args, esm_cube)
