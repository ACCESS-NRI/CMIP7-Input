from argparse import ArgumentParser
from pathlib import Path

from cmip7_ancil_argparse import common_parser
from cmip7_ancil_common import extend_years
from cmip7_ancil_constants import ANCIL_TODAY
from nitrogen.cmip7_nitrogen import (
    cmip7_nitrogen_dirpath,
    load_cmip7_nitrogen,
    regrid_cmip7_nitrogen,
    save_cmip7_nitrogen,
)


def parse_args():
    parser = ArgumentParser(
        parents=[common_parser()],
        prog="cmip7_HI_nitrogen_generate",
        description=(
            "Generate input files from CMIP7 historical nitrogen forcings"
        ),
    )
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_hi_nitrogen_filepath(args, species):
    dirpath = cmip7_nitrogen_dirpath(args, "mon", species)
    filename = (
        f"{species}_input4MIPs_surfaceFluxes_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}.nc"
    )
    return dirpath / filename


def esm_hi_nitrogen_save_dirpath(args):
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "historical"
        / "atmosphere"
        / "land"
        / "biogeochemistry"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


if __name__ == "__main__":
    args = parse_args()

    # Load the CMIP7 datasets
    nitrogen_cube = load_cmip7_nitrogen(args, cmip7_hi_nitrogen_filepath)
    # Regrid to match the ESM1.5 mask and extend the time series
    esm_cube = extend_years(regrid_cmip7_nitrogen(args, nitrogen_cube))
    # Save the ancillary
    save_cmip7_nitrogen(args, esm_cube, esm_hi_nitrogen_save_dirpath)
