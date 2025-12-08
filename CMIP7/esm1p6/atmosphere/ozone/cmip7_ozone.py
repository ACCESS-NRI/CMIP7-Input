from argparse import ArgumentParser

import iris
from cmip7_ancil_common import (
    INTERPOLATION_SCHEME,
    esm_grid_mask_cube,
    fix_coords,
)


def ozone_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--ukesm-ancil-dirpath")
    parser.add_argument("--ukesm-netcdf-filename")
    parser.add_argument("--save-filename")
    return parser


def cmip7_ozone_filepath(args):
    dirpath = args.ukesm_ancil_dirpath
    filename = args.ukesm_netcdf_filename
    return dirpath / filename


def load_cmip7_ozone(args):
    filepath = cmip7_ozone_filepath(args)
    cube = iris.load_cube(filepath)
    return cube


def regrid_cmip7_ozone(args, cube):
    # Make the coordinates comaptible with the ESM1.5 grid mask
    fix_coords(args, cube)
    # Regrid using the ESM1.5 grid mask
    esm_cube = cube.regrid(esm_grid_mask_cube(args), INTERPOLATION_SCHEME)
    esm_cube.data = esm_cube.data.filled(0.0)
    return esm_cube
