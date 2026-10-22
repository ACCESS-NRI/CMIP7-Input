# Interpolate CMIP7 HI SO2 emissions to ESM1.6 grid

from argparse import ArgumentParser
from functools import partial

from aerosol.cmip7_aerosol_anthro import anthro_variable
from aerosol.cmip7_HI_aerosol import (
    CMIP7_HI_AEROSOL_BEG_YEAR,
    CMIP7_HI_AEROSOL_END_YEAR,
    esm_hi_aerosol_ancil_dirpath,
    esm_hi_aerosol_save_dirpath,
)
from aerosol.cmip7_HI_aerosol_anthro import load_cmip7_hi_aerosol_anthro
from aerosol.cmip7_SO2_interpolate import (
    load_dms,
    save_cmip7_so2_aerosol_anthro,
)
from cmip7_ancil_argparse import (
    config_parser,
    dms_filename_parser,
    grid_parser,
    path_parser,
)
from cmip7_HI import fix_esm15_hi_ancil_date
from dataset import DatasetConfig

HI_DMS_ANCIL_FILENAME = "scycl_1849_2015_ESM1_v4.anc"


def parse_args():
    """Parse command-line arguments for historical SO2 emission interpolation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, config,
            DMS filename, and output filename parameters.
    """
    parser = ArgumentParser(
        prog="cmip7_HI_SO2_interpolate",
        description=("Generate input files from CMIP7 historical SO2 forcings"),
        parents=[
            path_parser(),
            grid_parser(),
            config_parser(),
            dms_filename_parser(dms_ancil_filename=HI_DMS_ANCIL_FILENAME),
        ],
    )
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_hi_so2_aerosol_anthro(args, config, species):
    """Load historical anthropogenic SO2 emissions covering the baseline years.

    Args:
        args (argparse.Namespace): Command-line arguments.
        config (dataset.DatasetConfig): Configuration of the surface
            emissions dataset, with its time range chunks.
        species (str): Target species ('SO2').

    Returns:
        iris.cube.Cube: Loaded SO2 emissions cube spanning 1849 to 2024.
    """
    return load_cmip7_hi_aerosol_anthro(
        args,
        config,
        species,
        beg_year=CMIP7_HI_AEROSOL_BEG_YEAR,
        end_year=CMIP7_HI_AEROSOL_END_YEAR,
    )


def load_hi_dms(args):
    """Load historical CMIP6 DMS ancillary dataset with 360-day calendar date
    fixes.

    Args:
        args (argparse.Namespace): Command-line arguments.

    Returns:
        iris.cube.Cube: Loaded DMS emissions cube.
    """
    # Use the CMIP6 DMS
    dms_ancil_dirpath = (
        esm_hi_aerosol_ancil_dirpath(args.esm15_inputs_dirname)
        / args.esm_grid_rel_dirname
        / args.esm15_aerosol_version
    )
    return load_dms(args, dms_ancil_dirpath, fix_esm15_hi_ancil_date)


if __name__ == "__main__":
    args = parse_args()
    config = DatasetConfig.from_yaml(args.config, section="anthro")

    save_cmip7_so2_aerosol_anthro(
        args,
        partial(load_cmip7_hi_so2_aerosol_anthro, args, config),
        config.to_dataset(variable_id=anthro_variable("SO2")),
        load_hi_dms,
        esm_hi_aerosol_save_dirpath(args),
    )
