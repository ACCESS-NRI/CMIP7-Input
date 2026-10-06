"""UKESM1 regridding utilities and coordinate fixing helpers for CMIP7
ancillaries.
"""

from argparse import ArgumentParser
from pathlib import Path

import iris
from cmip7_ancil_common import (
    fix_coords,
    fix_poles,
)

iris.FUTURE.datum_support = True


def ukesm_parser():
    """Create an argument parser for UKESM1 intermediate NetCDF datasets.

    Returns:
        argparse.ArgumentParser: Parser defining ``--ukesm-ancil-dirpath``,
            ``--ukesm-netcdf-filename``, and ``--save-filename``.
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--ukesm-ancil-dirpath")
    parser.add_argument("--ukesm-netcdf-filename")
    parser.add_argument("--save-filename")
    return parser


def cmip7_ukesm_filepath(args):
    """Construct the filesystem path to an intermediate UKESM1 NetCDF file.

    Args:
        args (argparse.Namespace): Parsed CLI arguments containing
            ``ukesm_ancil_dirpath`` and ``ukesm_netcdf_filename``.

    Returns:
        pathlib.Path: Full path to the UKESM NetCDF input file.
    """
    dirpath = Path(args.ukesm_ancil_dirpath)
    filename = args.ukesm_netcdf_filename
    return dirpath / filename


def load_cmip7_ukesm(args):
    """Load an intermediate UKESM1 forcing dataset into an Iris cube.

    Args:
        args (argparse.Namespace): Parsed CLI arguments containing file path
            parameters.

    Returns:
        iris.cube.Cube: Loaded UKESM forcing cube.
    """
    filepath = cmip7_ukesm_filepath(args)
    return iris.load_cube(filepath)


def fix_cmip7_ukesm(args, cube, fill=True):
    """Align UKESM1 cube coordinates with the ACCESS-ESM1.5 grid mask and
    resolve polar dependencies.

    Args:
        args (argparse.Namespace): Parsed CLI arguments containing grid
            configuration.
        cube (iris.cube.Cube): Input UKESM forcing cube.
        fill (bool, optional): If True, replaces masked values with 0.0.
            Defaults to True.

    Returns:
        iris.cube.Cube: Coordinate-corrected, polar-averaged Iris cube ready
            for ancillary file generation.
    """
    # Make the coordinates compatible with the ESM1.5 grid mask
    fix_coords(args, cube)
    if fill:
        cube.data = cube.data.filled(0.0)
    fix_poles(cube)
    return cube
