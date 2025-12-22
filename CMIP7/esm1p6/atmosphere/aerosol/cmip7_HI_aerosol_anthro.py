from argparse import ArgumentParser
from ast import literal_eval

from aerosol.cmip7_aerosol_anthro import (
    cmip7_aerosol_anthro_interpolate,
    load_cmip7_aerosol_anthro_list,
)
from aerosol.cmip7_HI_aerosol import esm_hi_aerosol_save_dirpath
from cmip7_ancil_argparse import common_parser
from cmip7_ancil_common import cmip7_date_constraint_from_years
from cmip7_HI import CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR


def parse_args(species):
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


def load_cmip7_hi_aerosol_anthro(
    args,
    species,
    beg_year=CMIP7_HI_BEG_YEAR,
    end_year=CMIP7_HI_END_YEAR,
):
    return load_cmip7_aerosol_anthro_list(
        args,
        species,
        args.dataset_date_range_list,
        cmip7_date_constraint_from_years(beg_year, end_year),
    )


def cmip7_hi_aerosol_anthro_interpolate(args, species, stash_item):
    cmip7_aerosol_anthro_interpolate(
        args,
        load_cmip7_hi_aerosol_anthro,
        species,
        stash_item,
        esm_hi_aerosol_save_dirpath(args),
    )
