from aerosol.cmip7_aerosol_anthro import (
        cmip7_aerosol_anthro_interpolate,
        load_cmip7_aerosol_anthro_list)
from aerosol.cmip7_HI_aerosol import (
        CMIP7_HI_AEROSOL_BEG_YEAR,
        CMIP7_HI_AEROSOL_END_YEAR,
        esm_hi_aerosol_save_dirpath)

from cmip7_ancil_argparse import (
        common_parser,
        constraint_year_parser)
from cmip7_ancil_common import cmip7_date_constraint_from_args

from argparse import ArgumentParser


def parse_args(species, save_filename):

    parser = ArgumentParser(
            prog=f'cmip7_HI_{species}_interpolate',
            description=(
                'Generate input files from CMIP7 historical '
                f'{species} forcings'),
            parents=[
                common_parser(),
                constraint_year_parser(
                    beg_year=CMIP7_HI_AEROSOL_BEG_YEAR,
                    end_year=CMIP7_HI_AEROSOL_END_YEAR)])
    parser.add_argument('--dataset-date-range-list', type=eval)
    parser.add_argument('--save-filename', default=save_filename)
    return parser.parse_args()


def load_cmip7_hi_aerosol_anthro(args, species):
    return load_cmip7_aerosol_anthro_list(
            args,
            species,
            args.dataset_date_range_list,
            cmip7_date_constraint_from_args(args))


def cmip7_hi_aerosol_anthro_interpolate(
        args,
        species,
        stash_item):
    cmip7_aerosol_anthro_interpolate(
            args,
            load_cmip7_hi_aerosol_anthro,
            species,
            stash_item,
            esm_hi_aerosol_save_dirpath(args))
