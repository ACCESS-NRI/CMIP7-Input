# Interpolate CMIP7 HI Biomass burning emissions to ESM1.6 grid

from aerosol.cmip7_aerosol_biomass import (
        load_cmip7_aerosol_biomass,
        load_cmip7_aerosol_biomass_list,
        save_cmip7_aerosol_biomass)
from aerosol.cmip7_HI_aerosol import (
        CMIP7_HI_AEROSOL_BEG_YEAR,
        CMIP7_HI_AEROSOL_END_YEAR,
        esm_hi_aerosol_save_dirpath)

from cmip7_ancil_argparse import (
        common_parser,
        constraint_year_parser,
        percent_parser)
from cmip7_ancil_common import cmip7_date_constraint_from_args

from argparse import ArgumentParser


def parse_args():

    SAVE_FILENAME = 'Bio_1849_2015_cmip7.anc'

    parser = ArgumentParser(
            prog='cmip7_HI_Bio_interpolate',
            description=(
                'Generate input files from CMIP7 historical biomass forcings'),
            parents=[
                common_parser(),
                percent_parser(),
                constraint_year_parser(
                    beg_year=CMIP7_HI_AEROSOL_BEG_YEAR,
                    end_year=CMIP7_HI_AEROSOL_END_YEAR)])
    parser.add_argument('--dataset-date-range-list', type=eval)
    parser.add_argument('--save-filename', default=SAVE_FILENAME)
    return parser.parse_args()


def load_cmip7_hi_aerosol_biomass(args, species):
    return load_cmip7_aerosol_biomass_list(
            args,
            species,
            args.dataset_date_range_list,
            cmip7_date_constraint_from_args(args))


def load_cmip7_hi_aerosol_biomass_percentage(args, species):
    return load_cmip7_aerosol_biomass(
            args,
            species,
            args.percent_date_range,
            cmip7_date_constraint_from_args(args))


if __name__ == '__main__':

    args = parse_args()

    save_cmip7_aerosol_biomass(
            args,
            load_cmip7_hi_aerosol_biomass_percentage,
            load_cmip7_hi_aerosol_biomass,
            esm_hi_aerosol_save_dirpath(args))
