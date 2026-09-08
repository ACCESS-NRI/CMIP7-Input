'''
    Generate the CMIP7 AMIP ancil file.
    This script loads the CMIP7 AMIP forcings, and then saves the ancil file in the specified directory.
'''
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
    '''
    Parse the command line arguments for CMIP7 AMIP forcings.
    '''
    parser = ArgumentParser(
        parents=[path_parser(), grid_parser(), ukesm_parser()],
        prog="cmip7_AM_amip_generate",
        description="Generate input files from UK CMIP7 AMIP forcings",
    )
    return parser.parse_args()


def esm_am_amip_save_dirpath(args):
    '''
    Return the directory path to save the ESM1.5 AMIP ancil files.'''
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
    '''
    Save the CMIP7 AMIP ancil file.
    '''
    # Save as an ancillary file
    save_dirpath = esm_am_amip_save_dirpath(args)
    save_ancil(
        cube,
        save_dirpath,
        args.save_filename,
        gregorian=False,
    )


if __name__ == "__main__":
    '''
    Generate the CMIP7 AMIP ancil file.
    '''
    args = parse_args()

    # Load the CMIP7 datasets
    ukesm_cube = load_cmip7_ukesm(args)
    # Match the ESM1.5 mask coordinates but do not zero-fill
    esm_cube = fix_cmip7_ukesm(args, ukesm_cube, fill=False)
    # Save the ancillary
    save_cmip7_am_amip(args, esm_cube)
