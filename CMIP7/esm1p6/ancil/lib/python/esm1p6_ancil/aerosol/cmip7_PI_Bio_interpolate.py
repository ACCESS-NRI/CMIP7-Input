# Interpolate CMIP7 PI Biomass burning emissions to ESM1.6 grid

from argparse import ArgumentParser

from aerosol.cmip7_aerosol_biomass import (
    load_cmip7_aerosol_biomass,
    save_cmip7_aerosol_biomass,
)
from aerosol.cmip7_PI_aerosol import esm_pi_aerosol_save_dirpath
from cmip7_ancil_argparse import common_parser, percent_parser
from cmip7_PI import cmip7_pi_date_constraint


def parse_args():
    """Parse command-line arguments for pre-industrial biomass burning emission
    interpolation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, percentage,
            date range, and output filename parameters.
    """
    parser = ArgumentParser(
        prog="cmip7_PI_Bio_interpolate",
        description=(
            "Generate input files from CMIP7 pre-industrial biomass forcings"
        ),
        parents=[common_parser(), percent_parser()],
    )
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_pi_aerosol_biomass(args, species):
    """Load pre-industrial biomass burning emissions for year 1850.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name ('BC' or 'OC').

    Returns:
        iris.cube.Cube: Loaded 12-month pre-industrial biomass emissions cube.
    """
    return load_cmip7_aerosol_biomass(
        args, species, args.dataset_date_range, cmip7_pi_date_constraint()
    )


def load_cmip7_pi_aerosol_biomass_percentage(args, species):
    """Load pre-industrial biomass burning percentage fractions for year 1850.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Percentage variable name (e.g. 'BCpercentageAGRI').

    Returns:
        iris.cube.Cube: Loaded 12-month percentage fraction cube.
    """
    return load_cmip7_aerosol_biomass(
        args, species, args.percent_date_range, cmip7_pi_date_constraint()
    )


if __name__ == "__main__":
    args = parse_args()

    save_cmip7_aerosol_biomass(
        args,
        load_cmip7_pi_aerosol_biomass_percentage,
        load_cmip7_pi_aerosol_biomass,
        esm_pi_aerosol_save_dirpath(args),
    )
