from argparse import ArgumentParser
from pathlib import Path

from cmip7_ancil_argparse import (
    grid_parser,
    path_parser,
)
from cmip7_ancil_common import save_ancil
from cmip7_ancil_constants import ANCIL_TODAY
from ozone.cmip7_ozone import (
    fix_cmip7_ozone,
    load_cmip7_ozone,
    ozone_parser,
)


def parse_args():
    """Parse command-line arguments for pre-industrial UKESM ozone ancillary
    generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, grid, and
            ozone dataset options.
    """
    parser = ArgumentParser(
        parents=[path_parser(), grid_parser(), ozone_parser()],
        prog="cmip7_PI_ozone_generate",
        description=(
            "Generate input files from UK CMIP7 pre-industrial ozone forcings"
        ),
    )
    return parser.parse_args()


def esm_pi_ozone_save_dirpath(args):
    """Construct the destination directory path for pre-industrial ozone
    ancillary files.

    Args:
        args (argparse.Namespace): Command-line arguments containing output
            path configuration (ancil_target_dirname, esm_grid_rel_dirname).

    Returns:
        pathlib.Path: Target directory path under modern/pre-
            industrial/atmosphere/forcing/.
    """
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "pre-industrial"
        / "atmosphere"
        / "forcing"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


def save_cmip7_pi_ozone(args, cube):
    """Write the processed pre-industrial ozone cube to an ancillary file with
    replaced bounds.

    Args:
        args (argparse.Namespace): Command-line arguments containing output
            path and filename.
        cube (iris.cube.Cube): Harmonized ozone cube to save.
    """
    # Save as an ancillary file
    save_dirpath = esm_pi_ozone_save_dirpath(args)
    save_ancil(cube, save_dirpath, args.save_filename, replace_bounds=True)


if __name__ == "__main__":
    args = parse_args()

    # Load the CMIP7 datasets
    ozone_cube = load_cmip7_ozone(args)
    # Match the ESM1.5 mask
    esm_cube = fix_cmip7_ozone(args, ozone_cube)
    # Save the ancillary
    save_cmip7_pi_ozone(args, esm_cube)
