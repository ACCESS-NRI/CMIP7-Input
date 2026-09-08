'''
    Interpolate CMIP7 ScenarioMIP SO2 emissions to ESM1.6 grid.
    This module provides a function to interpolate CMIP7 ScenarioMIP SO2 emissions data to the ESM1.6 grid.
    SO2 = Sulfur Dioxide.
'''
from argparse import ArgumentParser

from aerosol.cmip7_PI_aerosol import esm_pi_aerosol_ancil_dirpath
from aerosol.cmip7_PI_SO2_interpolate import PI_DMS_ANCIL_FILENAME
from aerosol.cmip7_SM_aerosol import esm_sm_aerosol_save_dirpath
from aerosol.cmip7_SM_aerosol_anthro import (
    cmip7_sm_aerosol_anthro_filepath,
    load_cmip7_sm_aerosol_anthro,
)
from aerosol.cmip7_SO2_interpolate import (
    load_dms,
    save_cmip7_so2_aerosol_anthro,
)
from cmip7_ancil_argparse import (
    common_parser,
    dms_filename_parser,
)
from cmip7_PI import fix_esm15_pi_ancil_date


def parse_args():
    '''
    Parse command line arguments for CMIP7 ScenarioMIP emissions SO2.
    '''
    parser = ArgumentParser(
        prog="cmip7_SM_SO2_interpolate",
        description=(
            "Generate input files from CMIP7 ScenarioMIP SO2 forcings"
        ),
        parents=[
            common_parser(),
            dms_filename_parser(dms_ancil_filename=PI_DMS_ANCIL_FILENAME),
        ],
    )
    parser.add_argument("--scenario")
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()

# TODO: Is it okay to not define this function?
def load_cmip7_sm_so2_aerosol_anthro(args, species):
    '''
    Load the CMIP7 ScenarioMIP emissions SO2 aerosol anthropogenic data for the given species and date range.
    '''
    return load_cmip7_sm_aerosol_anthro(args, species)


def load_sm_dms(args):
    '''
    Load the CMIP6 DMS ancillary data for the given date range.
    '''
    # Use the CMIP6 DMS
    dms_ancil_dirpath = (
        esm_pi_aerosol_ancil_dirpath(args.esm15_inputs_dirname)
        / args.esm_grid_rel_dirname
        / args.esm15_aerosol_version
    )
    return load_dms(args, dms_ancil_dirpath, fix_esm15_pi_ancil_date)


if __name__ == "__main__":
    '''
    Interpolate CMIP7 ScenarioMIP SO2 emissions to ESM1.6 grid.
    '''
    args = parse_args()

    save_cmip7_so2_aerosol_anthro(
        args,
        load_cmip7_sm_so2_aerosol_anthro,
        cmip7_sm_aerosol_anthro_filepath,
        args.dataset_date_range,
        load_sm_dms,
        esm_sm_aerosol_save_dirpath(args),
    )
