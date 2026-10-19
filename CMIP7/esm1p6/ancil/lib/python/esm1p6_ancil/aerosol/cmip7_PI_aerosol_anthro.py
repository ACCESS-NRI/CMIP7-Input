from argparse import ArgumentParser
from functools import partial

from aerosol.cmip7_aerosol_anthro import (
    cmip7_aerosol_anthro_interpolate,
    load_cmip7_aerosol_anthro,
)
from aerosol.cmip7_PI_aerosol import esm_pi_aerosol_save_dirpath
from cmip7_ancil_argparse import config_parser, grid_parser, path_parser
from cmip7_PI import cmip7_pi_date_constraint
from dataset import DatasetConfig


def parse_args(species):
    """Parse command-line arguments for pre-industrial aerosol emission
    interpolation.

    Args:
        species (str): Target aerosol species name.

    Returns:
        argparse.Namespace: Parsed CLI arguments.
    """
    parser = ArgumentParser(
        prog=f"cmip7_PI_{species}_interpolate",
        description=(
            f"Generate input files from CMIP7 pre-industrial {species} forcings"
        ),
        parents=[path_parser(), grid_parser(), config_parser()],
    )
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_pi_aerosol_anthro(args, config, species):
    """Load pre-industrial surface anthropogenic emissions for a given species
    for year 1850.

    Args:
        args (argparse.Namespace): Command-line arguments.
        config (dataset.DatasetConfig): Configuration of the surface
            emissions dataset.
        species (str): Aerosol species name.

    Returns:
        iris.cube.Cube: Loaded 12-month pre-industrial emissions cube.
    """
    return load_cmip7_aerosol_anthro(
        args, config, species, cmip7_pi_date_constraint()
    )


def cmip7_pi_aerosol_anthro_interpolate(args, species, stash_item):
    """Interpolate pre-industrial anthropogenic aerosol emissions and save to
    ancillary file.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        stash_item (int): UM STASH item number.
    """
    config = DatasetConfig.from_yaml(args.config, section="anthro")
    cmip7_aerosol_anthro_interpolate(
        args,
        partial(load_cmip7_pi_aerosol_anthro, args, config),
        species,
        stash_item,
        esm_pi_aerosol_save_dirpath(args),
    )
