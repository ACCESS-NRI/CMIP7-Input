# Interpolate CMIP7 HI SO2 emissions to ESM1.6 grid

from argparse import ArgumentParser
from ast import literal_eval

from aerosol.cmip7_PI_aerosol import esm_pi_aerosol_ancil_dirpath
from aerosol.cmip7_PI_SO2_interpolate import PI_DMS_ANCIL_FILENAME
from aerosol.cmip7_SM_aerosol import (
    CMIP7_SM_AEROSOL_BEG_YEAR,
    CMIP7_SM_AEROSOL_END_YEAR,
    esm_sm_aerosol_save_dirpath,
)
from aerosol.cmip7_SM_aerosol_anthro import load_cmip7_sm_aerosol_anthro
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
    parser = ArgumentParser(
        prog="cmip7_SM_SO2_interpolate",
        description=("Generate input files from CMIP7 historical SO2 forcings"),
        parents=[
            common_parser(),
            dms_filename_parser(dms_ancil_filename=PI_DMS_ANCIL_FILENAME),
        ],
    )
    parser.add_argument("--dataset-date-range-list", type=literal_eval)
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_sm_so2_aerosol_anthro(args, species):
    return load_cmip7_sm_aerosol_anthro(
        args,
        species,
        beg_year=CMIP7_SM_AEROSOL_BEG_YEAR,
        end_year=CMIP7_SM_AEROSOL_END_YEAR,
    )


def load_sm_dms(args):
    # Use the CMIP6 DMS
    dms_ancil_dirpath = (
        esm_pi_aerosol_ancil_dirpath(args.esm15_inputs_dirname)
        / args.esm_grid_rel_dirname
        / args.esm15_aerosol_version
    )
    return load_dms(args, dms_ancil_dirpath, fix_esm15_pi_ancil_date)


if __name__ == "__main__":
    args = parse_args()

    save_cmip7_so2_aerosol_anthro(
        args,
        load_cmip7_sm_so2_aerosol_anthro,
        args.dataset_date_range_list,
        load_sm_dms,
        esm_sm_aerosol_save_dirpath(args),
    )
