"""
Helpers for CMIP7 pre-industrial (PI) anthropogenic aerosol processing.

This module provides functions that connect the generic CMIP7 anthropogenic aerosol
interpolation workflow to the pre-industrial (PI) dataset selection.

"""

from argparse import ArgumentParser

from aerosol.cmip7_aerosol_anthro import (
    cmip7_aerosol_anthro_interpolate,
    load_cmip7_aerosol_anthro,
)
from aerosol.cmip7_PI_aerosol import esm_pi_aerosol_save_dirpath
from cmip7_ancil_argparse import common_parser
from cmip7_PI import cmip7_pi_date_constraint


def parse_args(species):
    """
    Parse command-line arguments for a PI aerosol interpolation task.
    """
    parser = ArgumentParser(
        prog=f"cmip7_PI_{species}_interpolate",
        description=(
            f"Generate input files from CMIP7 pre-industrial {species} forcings"
        ),
        parents=[common_parser()],
    )
    # The dataset selector used to choose which percentage/ancil input to load.
    parser.add_argument("--dataset-date-range")
    # Output filename for the generated ancillary file.
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_pi_aerosol_anthro(args, species):
    """
    Load the CMIP7 PI anthropogenic aerosol cube for the given species.
    """
    return load_cmip7_aerosol_anthro(
        args, species, args.dataset_date_range, cmip7_pi_date_constraint()
    )


def cmip7_pi_aerosol_anthro_interpolate(args, species, stash_item):
    """
    Run the shared interpolate/save pipeline for PI anthropogenic aerosols.

    This function performs the aggregation, regridding, missing-value/pole cleanup, 
    STASH tagging and save steps.
    """
    cmip7_aerosol_anthro_interpolate(
        args,
        load_cmip7_pi_aerosol_anthro,
        species,
        stash_item,
        esm_pi_aerosol_save_dirpath(args),
    )
