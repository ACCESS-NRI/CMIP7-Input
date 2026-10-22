# Interpolate CMIP7 PI Biomass burning emissions to ESM1.6 grid

from argparse import ArgumentParser
from functools import partial

from aerosol.cmip7_aerosol_biomass import (
    load_cmip7_aerosol_biomass,
    save_cmip7_aerosol_biomass,
)
from aerosol.cmip7_PI_aerosol import esm_pi_aerosol_save_dirpath
from cmip7_ancil_argparse import config_parser, grid_parser, path_parser
from cmip7_PI import cmip7_pi_date_constraint
from dataset import DatasetConfig


def parse_args():
    """Parse command-line arguments for pre-industrial biomass burning emission
    interpolation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, config,
            and output filename parameters.
    """
    parser = ArgumentParser(
        prog="cmip7_PI_Bio_interpolate",
        description=(
            "Generate input files from CMIP7 pre-industrial biomass forcings"
        ),
        parents=[path_parser(), grid_parser(), config_parser()],
    )
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_pi_aerosol_biomass(config, species):
    """Load pre-industrial biomass burning emissions for year 1850.

    Args:
        config (dataset.DatasetConfig): Configuration of the biomass
            burning emissions dataset, or of the percentage fractions
            dataset.
        species (str): Variable name ('BC', 'OC', or a percentage variable
            such as 'BCpercentageAGRI').

    Returns:
        iris.cube.Cube: Loaded 12-month pre-industrial biomass cube.
    """
    return load_cmip7_aerosol_biomass(
        config, species, cmip7_pi_date_constraint()
    )


if __name__ == "__main__":
    args = parse_args()
    config = DatasetConfig.from_yaml(args.config, section="biomass")
    pc_config = DatasetConfig.from_yaml(
        args.config, section="biomass-percentage"
    )

    save_cmip7_aerosol_biomass(
        args,
        partial(load_cmip7_pi_aerosol_biomass, pc_config),
        partial(load_cmip7_pi_aerosol_biomass, config),
        esm_pi_aerosol_save_dirpath(args),
    )
