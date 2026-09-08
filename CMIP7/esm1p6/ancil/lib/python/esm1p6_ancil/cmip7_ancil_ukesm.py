from argparse import ArgumentParser
from pathlib import Path

import iris
from cmip7_ancil_common import (
    fix_coords,
    fix_poles,
)

# TODO: This is the exact same parser as in cmip7_ancil_ozone.py. Consider refactoring to avoid code duplication.
def ukesm_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--ukesm-ancil-dirpath")
    parser.add_argument("--ukesm-netcdf-filename")
    parser.add_argument("--save-filename")
    return parser

# TODO: This is the exact same function as in cmip7_ancil_ozone.py. Consider refactoring to avoid code duplication.
def cmip7_ukesm_filepath(args):
    dirpath = Path(args.ukesm_ancil_dirpath)
    filename = args.ukesm_netcdf_filename
    return dirpath / filename

# TODO: This is the exact same function as in cmip7_ancil_ozone.py. Consider refactoring to avoid code duplication.
def load_cmip7_ukesm(args):
    filepath = cmip7_ukesm_filepath(args)
    return iris.load_cube(filepath)

# TODO: This is the exact same function as in cmip7_ancil_ozone.py. Except for the fix_poles() call and the fill parameter. Consider refactoring to avoid code duplication.
def fix_cmip7_ukesm(args, cube, fill=True):
    # Make the coordinates compatible with the ESM1.5 grid mask
    fix_coords(args, cube)
    if fill:
        cube.data = cube.data.filled(0.0)
    fix_poles(cube)
    return cube
