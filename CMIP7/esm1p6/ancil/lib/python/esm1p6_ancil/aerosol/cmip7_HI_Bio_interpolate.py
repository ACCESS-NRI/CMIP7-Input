# Interpolate CMIP7 HI Biomass burning emissions to ESM1.6 grid

from argparse import ArgumentParser
from ast import literal_eval

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
from cmip7_ancil_argparse import (
    common_parser,
    percent_parser,
)
from cmip7_ancil_common import cmip7_date_constraint_from_years


def parse_args():
    '''
    Parse command line arguments for CMIP7 historical emissions aerosol biomass burning.
    '''
    parser = ArgumentParser(
        prog="cmip7_HI_Bio_interpolate",
        description=(
            "Generate input files from CMIP7 historical biomass forcings"
        ),
        parents=[
            common_parser(),
            percent_parser(),
        ],
    )
    parser.add_argument("--dataset-date-range-list", type=literal_eval)
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_hi_aerosol_biomass(args, species):
    '''
    Load the CMIP7 historical emissions aerosol biomass burning data for the given species and date range.
    '''
    return load_cmip7_aerosol_biomass_list(
        args,
        species,
        args.dataset_date_range_list,
        cmip7_date_constraint_from_years(
            CMIP7_HI_AEROSOL_BEG_YEAR,
            CMIP7_HI_AEROSOL_END_YEAR,
        ),
    )


def load_cmip7_hi_aerosol_biomass_percentage(args, species):
    '''
    Load the CMIP7 historical emissions aerosol biomass burning data for the given species and date range percentage. (It is given as a date range percentage, e.g. '175001-202312')
    '''
    return load_cmip7_aerosol_biomass(
        args,
        species,
        args.percent_date_range,
        cmip7_date_constraint_from_years(
            CMIP7_HI_AEROSOL_BEG_YEAR,
            CMIP7_HI_AEROSOL_END_YEAR,
        ),
    )


if __name__ == "__main__":
    '''
    Interpolate CMIP7 historical emissions aerosol biomass burning data to the ESM1.6 grid.
    '''
    args = parse_args()

    save_cmip7_aerosol_biomass(
        args,
        load_cmip7_hi_aerosol_biomass_percentage,
        load_cmip7_hi_aerosol_biomass,
        esm_hi_aerosol_save_dirpath(args),
    )
