from argparse import ArgumentParser
from pathlib import Path

from cmip7_ancil_argparse import common_parser
from cmip7_ancil_constants import ANCIL_TODAY
from nitrogen.cmip7_nitrogen import (
    cmip7_nitrogen_dirpath,
    load_cmip7_nitrogen,
    regrid_cmip7_nitrogen,
    save_cmip7_nitrogen,
)


def parse_args():
    """Parse command-line arguments for pre-industrial nitrogen ancillary
    generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, grid,
            dataset, date range, and save filename parameters.
    """
    parser = ArgumentParser(
        parents=[common_parser()],
        prog="cmip7_PI_nitrogen_generate",
        description=(
            "Generate input files from CMIP7 pre-industrial nitrogen forcings"
        ),
    )
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_pi_nitrogen_filepath(args, species):
    """Construct the file path for a pre-industrial climatological nitrogen
    netCDF dataset.

    Args:
        args (argparse.Namespace): Command-line arguments containing dataset
            configuration.
        species (str): Reactive nitrogen species identifier.

    Returns:
        pathlib.Path: File path to the climatological (monC) input4MIPs netCDF
            file.
    """
    dirpath = cmip7_nitrogen_dirpath(args, "CMIP", "monC", species)
    filename = (
        f"{species}_input4MIPs_surfaceFluxes_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}-clim.nc"
    )
    return dirpath / filename


def esm_pi_nitrogen_save_dirpath(args):
    """Construct the destination directory path for pre-industrial nitrogen
    ancillary files.

    Args:
        args (argparse.Namespace): Command-line arguments containing output
            path configuration.

    Returns:
        pathlib.Path: Target directory path under modern/pre-
            industrial/atmosphere/land/biogeochemistry/.
    """
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "pre-industrial"
        / "atmosphere"
        / "land"
        / "biogeochemistry"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


if __name__ == "__main__":
    args = parse_args()

    # Load the CMIP7 datasets
    nitrogen_cube = load_cmip7_nitrogen(args, cmip7_pi_nitrogen_filepath)
    # Regrid to match the ESM1.5 mask
    esm_cube = regrid_cmip7_nitrogen(args, nitrogen_cube)
    # Save the ancillary
    save_cmip7_nitrogen(args, esm_cube, esm_pi_nitrogen_save_dirpath)
