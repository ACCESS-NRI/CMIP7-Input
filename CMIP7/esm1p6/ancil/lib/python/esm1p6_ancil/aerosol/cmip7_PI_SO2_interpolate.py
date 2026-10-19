# Interpolate CMIP7 PI SO2 emissions to ESM1.6 grid

from argparse import ArgumentParser
from functools import partial

from aerosol.cmip7_aerosol_anthro import anthro_variable
from aerosol.cmip7_PI_aerosol import (
    esm_pi_aerosol_ancil_dirpath,
    esm_pi_aerosol_save_dirpath,
)
from aerosol.cmip7_PI_aerosol_anthro import load_cmip7_pi_aerosol_anthro
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
from cmip7_PI import fix_esm15_pi_ancil_date
from dataset import DatasetConfig

PI_DMS_ANCIL_FILENAME = "scycl_1850_ESM1_v4.anc"


def parse_args():
    """Parse command-line arguments for pre-industrial SO2 emission
    interpolation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, config,
            DMS filename, and output filename parameters.
    """
    parser = ArgumentParser(
        prog="cmip7_PI_SO2_interpolate",
        description=(
            "Generate input files from CMIP7 pre-industrial SO2 forcings"
        ),
        parents=[
            path_parser(),
            grid_parser(),
            config_parser(),
            dms_filename_parser(dms_ancil_filename=PI_DMS_ANCIL_FILENAME),
        ],
    )
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_pi_dms(args):
    """Load pre-industrial CMIP6 DMS ancillary dataset with 360-day calendar
    date fixes.

    Args:
        args (argparse.Namespace): Command-line arguments.

    Returns:
        iris.cube.Cube: Loaded DMS emissions cube.
    """
    # Use the CMIP6 DMS
    dms_ancil_dirpath = (
        esm_pi_aerosol_ancil_dirpath(args.esm15_inputs_dirname)
        / args.esm_grid_rel_dirname
        / args.esm15_aerosol_version
    )
    return load_dms(args, dms_ancil_dirpath, fix_esm15_pi_ancil_date)


if __name__ == "__main__":
    args = parse_args()
    config = DatasetConfig.from_yaml(args.config, section="anthro")

    save_cmip7_so2_aerosol_anthro(
        args,
        partial(load_cmip7_pi_aerosol_anthro, args, config),
        config.to_dataset(variable_id=anthro_variable("SO2")),
        load_pi_dms,
        esm_pi_aerosol_save_dirpath(args),
    )
