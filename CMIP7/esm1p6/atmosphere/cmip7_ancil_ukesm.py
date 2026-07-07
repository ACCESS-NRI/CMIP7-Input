from argparse import ArgumentParser
from pathlib import Path

import iris
from cmip7_ancil_common import (
    fix_coords,
    fix_poles,
)


def ukesm_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--ukesm-ancil-dirpath")
    parser.add_argument("--ukesm-netcdf-filename")
    parser.add_argument("--save-filename")
    return parser


def cmip7_ukesm_filepath(args):
    dirpath = Path(args.ukesm_ancil_dirpath)
    filename = args.ukesm_netcdf_filename
    return dirpath / filename


def load_cmip7_ukesm(args):
    filepath = cmip7_ukesm_filepath(args)
    return iris.load_cube(filepath)


def fix_cmip7_ukesm(args, cube, fill=True):
    # Make the coordinates compatible with the ESM1.5 grid mask
    fix_coords(args, cube)
    if fill:
        cube.data = cube.data.filled(0.0)
    print(cube)
    print(type(cube.data))
    fix_poles(cube)
    return cube
