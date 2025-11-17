# Interpolate CMIP7 HI SO2 emissions to ESM1.6 grid

from argparse import ArgumentParser
from ast import literal_eval

from esm1p6_ancil.aerosol.cmip7_HI_aerosol import (
    CMIP7_HI_AEROSOL_BEG_YEAR,
    CMIP7_HI_AEROSOL_END_YEAR,
    esm_hi_aerosol_ancil_dirpath,
    esm_hi_aerosol_save_dirpath,
)
from esm1p6_ancil.aerosol.cmip7_HI_aerosol_anthro import load_cmip7_hi_aerosol_anthro
from esm1p6_ancil.aerosol.cmip7_SO2_interpolate import (
    load_dms,
    save_cmip7_so2_aerosol_anthro,
)
from esm1p6_ancil.cmip7_ancil_argparse import (
    common_parser,
    dms_filename_parser,
)
from esm1p6_ancil.cmip7_HI import fix_esm15_hi_ancil_date


def parse_args():
    DMS_ANCIL_FILENAME = "scycl_1849_2015_ESM1_v4.anc"

    parser = ArgumentParser(
        prog="cmip7_HI_SO2_interpolate",
        description=("Generate input files from CMIP7 historical SO2 forcings"),
        parents=[
            common_parser(),
            dms_filename_parser(dms_ancil_filename=DMS_ANCIL_FILENAME),
        ],
    )
    parser.add_argument("--dataset-date-range-list", type=literal_eval)
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_hi_so2_aerosol_anthro(args, species):
    return load_cmip7_hi_aerosol_anthro(
        args,
        species,
        beg_year=CMIP7_HI_AEROSOL_BEG_YEAR,
        end_year=CMIP7_HI_AEROSOL_END_YEAR,
    )


def load_hi_dms(args):
    # Use the CMIP6 DMS
    dms_ancil_dirpath = (
        esm_hi_aerosol_ancil_dirpath(args.esm15_inputs_dirname)
        / args.esm_grid_rel_dirname
        / args.esm15_aerosol_version
    )
    return load_dms(args, dms_ancil_dirpath, fix_esm15_hi_ancil_date)


if __name__ == "__main__":
    args = parse_args()

    save_cmip7_so2_aerosol_anthro(
        args,
        load_cmip7_hi_so2_aerosol_anthro,
        args.dataset_date_range_list,
        load_hi_dms,
        esm_hi_aerosol_save_dirpath(args),
    )
