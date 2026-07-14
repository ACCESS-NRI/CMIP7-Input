from argparse import ArgumentParser
from pathlib import Path

import iris
from cmip7_ancil_common import fix_coords


def ozone_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--ukesm-ancil-dirpath")
    parser.add_argument("--ukesm-netcdf-filename")
    parser.add_argument("--save-filename")
    return parser


def cmip7_ozone_filepath(args):
    dirpath = Path(args.ukesm_ancil_dirpath)
    filename = args.ukesm_netcdf_filename
    return dirpath / filename


def load_cmip7_ozone(args):
    filepath = cmip7_ozone_filepath(args)
    cube = iris.load_cube(filepath)
    return cube


def fix_cmip7_ozone(args, cube):
    # Make the coordinates compatible with the ESM1.5 grid mask
    fix_coords(args, cube)
    cube.data = cube.data.filled(0.0)
    return cube
