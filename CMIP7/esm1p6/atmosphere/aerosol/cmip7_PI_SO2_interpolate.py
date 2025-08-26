# Interpolate CMIP7 PI SO2 emissions to ESM1.6 grid

from aerosol.cmip7_PI_aerosol import (
        esm_pi_aerosol_ancil_dirpath,
        esm_pi_aerosol_save_dirpath)
from aerosol.cmip7_PI_aerosol_anthro import load_cmip7_pi_aerosol_anthro
from aerosol.cmip7_SO2_interpolate import (
        load_dms,
        save_cmip7_so2_aerosol_anthro)

from cmip7_ancil_argparse import (
        common_parser,
        dms_filename_parser)
from cmip7_PI import fix_esm15_pi_ancil_date

from argparse import ArgumentParser


def parse_args():

    DMS_ANCIL_FILENAME = 'scycl_1850_ESM1_v4.anc'

    parser = ArgumentParser(
            prog='cmip7_PI_SO2_interpolate',
            description=(
                'Generate input files from CMIP7 pre-industrial SO2 forcings'),
            parents=[
                common_parser(),
                dms_filename_parser(dms_ancil_filename=DMS_ANCIL_FILENAME)])
    parser.add_argument('--dataset-date-range')
    parser.add_argument('--save-filename')
    return parser.parse_args()


def load_pi_dms(args):
    # Use the CMIP6 DMS
    dms_ancil_dirpath = (
            esm_pi_aerosol_ancil_dirpath(args.esm15_inputs_dirname)
            / args.esm_grid_rel_dirname
            / args.esm15_aerosol_version)
    return load_dms(
            args,
            dms_ancil_dirpath,
            fix_esm15_pi_ancil_date)


if __name__ == '__main__':

    args = parse_args()

    save_cmip7_so2_aerosol_anthro(
            args,
            load_cmip7_pi_aerosol_anthro,
            args.dataset_date_range,
            load_pi_dms,
            esm_pi_aerosol_save_dirpath(args))
