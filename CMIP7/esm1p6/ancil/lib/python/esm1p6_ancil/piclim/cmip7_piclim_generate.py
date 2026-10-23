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
from iris.time import PartialDateTime
from iris import Constraint


def parse_args():
    parser = ArgumentParser(
        parents=[path_parser(), grid_parser(), ukesm_parser()],
        prog="cmip7_AM_piclim_generate",
        description="Generate input files from UK CMIP7 AMIP forcings",
    )
    return parser.parse_args()


def esm_am_amip_save_dirpath(args):
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "piclim"
        / "atmosphere"
        / "boundary_conditions"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


def save_cmip7_am_amip(args, cube):
    # Save as an ancillary file
    save_dirpath = esm_am_amip_save_dirpath(args)
    save_ancil(
        cube,
        save_dirpath,
        args.save_filename,
        replace_bounds=True,
        gregorian=True,
        # time_type=2
    )


if __name__ == "__main__":
    args = parse_args()

    # Load the CMIP7 datasets
    ukesm_cube = load_cmip7_ukesm(args)
    # Match the ESM1.5 mask coordinates but do not zero-fill
    esm_cube = fix_cmip7_ukesm(args, ukesm_cube, fill=False)
    # Subset to one year in the middle of the period
    time_constraint = Constraint(time=lambda cell: cell.point==PartialDateTime(year=1950))
    tmp_cube = esm_cube.extract(time_constraint)
    # Add time bounds. This gives incorrect results but overwritten later by set_gregorian
    tmp_cube.coord('time').guess_bounds()
    # Save the ancillary
    save_cmip7_am_amip(args, tmp_cube) # esm_cube.extract(time_constraint))
