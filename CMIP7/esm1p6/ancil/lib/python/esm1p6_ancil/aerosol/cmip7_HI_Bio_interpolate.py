# Interpolate CMIP7 HI Biomass burning emissions to ESM1.6 grid

from argparse import ArgumentParser
from functools import partial

from aerosol.cmip7_aerosol_biomass import (
    load_cmip7_aerosol_biomass,
    load_cmip7_aerosol_biomass_list,
    save_cmip7_aerosol_biomass,
)
from aerosol.cmip7_HI_aerosol import (
    CMIP7_HI_AEROSOL_BEG_YEAR,
    CMIP7_HI_AEROSOL_END_YEAR,
    esm_hi_aerosol_save_dirpath,
)
from cmip7_ancil_argparse import config_parser, grid_parser, path_parser
from cmip7_ancil_common import cmip7_date_constraint_from_years
from dataset import DatasetConfig


def parse_args():
    """Parse command-line arguments for historical biomass burning emission
    interpolation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, config,
            and output filename parameters.
    """
    parser = ArgumentParser(
        prog="cmip7_HI_Bio_interpolate",
        description=(
            "Generate input files from CMIP7 historical biomass forcings"
        ),
        parents=[path_parser(), grid_parser(), config_parser()],
    )
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_hi_aerosol_biomass(config, species):
    """Load historical biomass burning emissions for a species across all date
    range chunks.

    Args:
        config (dataset.DatasetConfig): Configuration of the biomass
            burning emissions dataset, with its time range chunks.
        species (str): Aerosol species name ('BC' or 'OC').

    Returns:
        iris.cube.Cube: Loaded continuous biomass emissions cube spanning 1849
            to 2024.
    """
    return load_cmip7_aerosol_biomass_list(
        config,
        species,
        cmip7_date_constraint_from_years(
            CMIP7_HI_AEROSOL_BEG_YEAR,
            CMIP7_HI_AEROSOL_END_YEAR,
        ),
    )


def load_cmip7_hi_aerosol_biomass_percentage(config, species):
    """Load historical biomass burning percentage fractions for a given fire
    source.

    Args:
        config (dataset.DatasetConfig): Configuration of the percentage
            fractions dataset, with a single time range.
        species (str): Percentage variable name (e.g. 'BCpercentageAGRI').

    Returns:
        iris.cube.Cube: Loaded percentage fraction cube.
    """
    return load_cmip7_aerosol_biomass(
        config,
        species,
        cmip7_date_constraint_from_years(
            CMIP7_HI_AEROSOL_BEG_YEAR,
            CMIP7_HI_AEROSOL_END_YEAR,
        ),
    )


if __name__ == "__main__":
    args = parse_args()
    config = DatasetConfig.from_yaml(args.config, section="biomass")
    pc_config = DatasetConfig.from_yaml(
        args.config, section="biomass-percentage"
    )

    save_cmip7_aerosol_biomass(
        args,
        partial(load_cmip7_hi_aerosol_biomass_percentage, pc_config),
        partial(load_cmip7_hi_aerosol_biomass, config),
        esm_hi_aerosol_save_dirpath(args),
    )
