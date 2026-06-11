# Interpolate CMIP7 HI Biomass burning emissions to ESM1.6 grid

from argparse import ArgumentParser

from aerosol.cmip7_aerosol_biomass import (
    load_cmip7_aerosol_biomass,
    save_cmip7_aerosol_biomass,
)
from aerosol.cmip7_SM_aerosol import (
    CMIP7_SM_AEROSOL_BEG_YEAR,
    CMIP7_SM_AEROSOL_END_YEAR,
    esm_sm_aerosol_save_dirpath,
)
from cmip7_ancil_argparse import (
    common_parser,
    percent_parser,
)
from cmip7_ancil_common import cmip7_date_constraint_from_years


def parse_args():
    parser = ArgumentParser(
        prog="cmip7_SM_Bio_interpolate",
        description=(
            "Generate input files from CMIP7 historical biomass forcings"
        ),
        parents=[
            common_parser(),
            percent_parser(),
        ],
    )
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_sm_aerosol_biomass(args, species):
    return load_cmip7_aerosol_biomass(
        args,
        species,
        args.dataset_date_range,
        cmip7_date_constraint_from_years(
            CMIP7_SM_AEROSOL_BEG_YEAR,
            CMIP7_SM_AEROSOL_END_YEAR,
        ),
    )


def load_cmip7_sm_aerosol_biomass_percentage(args, species):
    return load_cmip7_aerosol_biomass(
        args,
        species,
        args.percent_date_range,
        cmip7_date_constraint_from_years(
            CMIP7_SM_AEROSOL_BEG_YEAR,
            CMIP7_SM_AEROSOL_END_YEAR,
        ),
    )


if __name__ == "__main__":
    args = parse_args()

    save_cmip7_aerosol_biomass(
        args,
        load_cmip7_sm_aerosol_biomass_percentage,
        load_cmip7_sm_aerosol_biomass,
        esm_sm_aerosol_save_dirpath(args),
    )
