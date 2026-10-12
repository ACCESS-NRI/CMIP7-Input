from argparse import ArgumentParser
from pathlib import Path

import iris
from cmip7_ancil_common import fix_coords

iris.FUTURE.datum_support = True


def ozone_parser():
    """Create an argument parser with common options for UKESM ozone ancillary
    datasets.

    Returns:
        argparse.ArgumentParser: Argument parser providing --ukesm-ancil-
            dirpath, --ukesm-netcdf-filename, and --save-filename.
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--ukesm-ancil-dirpath")
    parser.add_argument("--ukesm-netcdf-filename")
    parser.add_argument("--save-filename")
    return parser


def cmip7_ozone_filepath(args):
    """Construct the file path to the UKESM netCDF ozone input file.

    Args:
        args (argparse.Namespace): Command-line arguments containing
            ukesm_ancil_dirpath and ukesm_netcdf_filename.

    Returns:
        pathlib.Path: Path to the input ozone netCDF file.
    """
    dirpath = Path(args.ukesm_ancil_dirpath)
    filename = args.ukesm_netcdf_filename
    return dirpath / filename


def load_cmip7_ozone(args):
    """Load the UKESM ozone concentration netCDF dataset into an Iris cube.

    Args:
        args (argparse.Namespace): Command-line arguments specifying the input
            dataset path.

    Returns:
        iris.cube.Cube: Loaded ozone concentration cube.
    """
    filepath = cmip7_ozone_filepath(args)
    cube = iris.load_cube(filepath)
    return cube


def fix_cmip7_ozone(args, cube):
    """Align ozone cube coordinates with the target model grid mask and fill
    masked values.

    Args:
        args (argparse.Namespace): Command-line arguments specifying grid
            configuration.
        cube (iris.cube.Cube): Input ozone cube.

    Returns:
        iris.cube.Cube: Harmonized cube with unified coordinate metadata and
            zero-filled missing data.
    """
    # Make the coordinates compatible with the ESM1.5 grid mask
    fix_coords(args, cube)
    cube.data = cube.data.filled(0.0)
    return cube
