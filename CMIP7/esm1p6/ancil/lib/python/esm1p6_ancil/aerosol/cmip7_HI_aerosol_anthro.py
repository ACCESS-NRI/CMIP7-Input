from argparse import ArgumentParser
from ast import literal_eval

from aerosol.cmip7_aerosol_anthro import (
    cmip7_aerosol_anthro_interpolate,
    load_cmip7_aerosol_air_anthro_list,
    load_cmip7_aerosol_anthro_list,
)
from aerosol.cmip7_HI_aerosol import (
    CMIP7_HI_AEROSOL_BEG_YEAR,
    CMIP7_HI_AEROSOL_END_YEAR,
    esm_hi_aerosol_save_dirpath,
)
from cmip7_ancil_argparse import common_parser
from cmip7_ancil_common import cmip7_date_constraint_from_years


def parse_args(species):
    """Parse command-line arguments for historical aerosol emission
    interpolation.

    Args:
        species (str): Target aerosol species name.

    Returns:
        argparse.Namespace: Parsed CLI arguments.
    """
    parser = ArgumentParser(
        prog=f"cmip7_HI_{species}_interpolate",
        description=(
            f"Generate input files from CMIP7 historical {species} forcings"
        ),
        parents=[common_parser()],
    )
    parser.add_argument("--dataset-date-range-list", type=literal_eval)
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_hi_aerosol_air_anthro(
    args,
    species,
    beg_year=CMIP7_HI_AEROSOL_BEG_YEAR,
    end_year=CMIP7_HI_AEROSOL_END_YEAR,
):
    """Load historical aircraft emissions for a given species constrained to
    year range.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        beg_year (int, optional): Start year. Defaults to 1849.
        end_year (int, optional): End year. Defaults to 2024.

    Returns:
        iris.cube.Cube: Loaded aircraft emissions cube.
    """
    return load_cmip7_aerosol_air_anthro_list(
        args,
        species,
        args.dataset_date_range_list,
        cmip7_date_constraint_from_years(beg_year, end_year),
    )


def load_cmip7_hi_aerosol_anthro(
    args,
    species,
    beg_year=CMIP7_HI_AEROSOL_BEG_YEAR,
    end_year=CMIP7_HI_AEROSOL_END_YEAR,
):
    """Load historical surface emissions for a given species constrained to
    year range.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        beg_year (int, optional): Start year. Defaults to 1849.
        end_year (int, optional): End year. Defaults to 2024.

    Returns:
        iris.cube.Cube: Loaded surface emissions cube.
    """
    return load_cmip7_aerosol_anthro_list(
        args,
        species,
        args.dataset_date_range_list,
        cmip7_date_constraint_from_years(beg_year, end_year),
    )


def cmip7_hi_aerosol_anthro_interpolate(args, species, stash_item):
    """Interpolate historical anthropogenic aerosol emissions and save to
    ancillary file.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        stash_item (int): UM STASH item number.
    """
    cmip7_aerosol_anthro_interpolate(
        args,
        load_cmip7_hi_aerosol_anthro,
        species,
        stash_item,
        esm_hi_aerosol_save_dirpath(args),
    )
