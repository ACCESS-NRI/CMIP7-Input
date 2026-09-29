from argparse import ArgumentParser
from pathlib import Path

from cmip7_ancil_argparse import (
    grid_parser,
    path_parser,
)
from cmip7_ancil_common import save_ancil
from cmip7_ancil_constants import ANCIL_TODAY
from cmip7_ancil_ukesm import (
    fix_cmip7_ukesm,
    load_cmip7_ukesm,
    ukesm_parser,
)


def parse_args():
    """Parse command-line arguments for UK CMIP7 AMIP ancillary generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, grid, and
            UKESM options.
    """
    parser = ArgumentParser(
        parents=[path_parser(), grid_parser(), ukesm_parser()],
        prog="cmip7_AM_amip_generate",
        description="Generate input files from UK CMIP7 AMIP forcings",
    )
    return parser.parse_args()


def esm_am_amip_save_dirpath(args):
    """Construct the destination directory path for AMIP SST and sea-ice
    ancillary files.

    Args:
        args (argparse.Namespace): Command-line arguments containing output
            path configuration (ancil_target_dirname, esm_grid_rel_dirname).

    Returns:
        pathlib.Path: Target directory path under
            modern/amip/atmosphere/boundary_conditions/.
    """
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "amip"
        / "atmosphere"
        / "boundary_conditions"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


def save_cmip7_am_amip(args, cube):
    """Write the AMIP boundary condition cube to an ancillary file (360-day
    calendar).

    Args:
        args (argparse.Namespace): Command-line arguments containing output
            path and filename.
        cube (iris.cube.Cube): Harmonized AMIP cube.
    """
    # Save as an ancillary file
    save_dirpath = esm_am_amip_save_dirpath(args)
    save_ancil(
        cube,
        save_dirpath,
        args.save_filename,
        gregorian=False,
    )


if __name__ == "__main__":
    args = parse_args()

    # Load the CMIP7 datasets
    ukesm_cube = load_cmip7_ukesm(args)
    # Match the ESM1.5 mask coordinates but do not zero-fill
    esm_cube = fix_cmip7_ukesm(args, ukesm_cube, fill=False)
    # Save the ancillary
    save_cmip7_am_amip(args, esm_cube)
