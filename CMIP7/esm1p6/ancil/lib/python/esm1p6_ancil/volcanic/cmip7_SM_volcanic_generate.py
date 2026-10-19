from argparse import ArgumentParser

from cmip7_ancil_argparse import (
    config_parser,
    ext_parser,
    pad_parser,
    path_parser,
)
from cmip7_SM import CMIP7_SM_EXT_END_YEAR, esm_sm_forcing_save_dirpath
from dataset import DatasetConfig
from volcanic.cmip7_PI_volcanic_generate import (
    average_stratospheric_aerosol_optical_depth,
)
from volcanic.cmip7_volcanic import (
    SAOD_SCALING,
    save_stratospheric_aerosol_optical_depth,
)

CMIP7_SM_VOLCANIC_BEG_YEAR = 2022
CMIP7_SM_VOLCANIC_END_YEAR = 2100


def parse_args():
    """Parse command-line arguments for ScenarioMIP volcanic forcing
    generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, config, pad,
            ext, scenario, and save filename.
    """
    parser = ArgumentParser(
        prog="cmip7_SM_volcanic_generate",
        description=(
            "Generate input files from CMIP7 ScenarioMIP volcanic forcings"
        ),
        parents=[
            path_parser(),
            config_parser(),
            pad_parser(),
            ext_parser(),
        ],
    )
    parser.add_argument("--scenario")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def save_sm_stratospheric_aerosol_optical_depth(
    args, dataset_path, pi_mean_saod
):
    """Calculate the average stratospheric aerosol optical depth (SAOD)
    for each historical month by averaging extinction over latitude,
    and summing over stratospheric layers. Save to the save file.

    Args:
        args (argparse.Namespace): Command-line arguments specifying pad, ext,
            and output options.
        dataset_path (os.PathLike): Path to the ScenarioMIP volcanic
            extinction netCDF file.
        pi_mean_saod (float): Pre-industrial mean SAOD constant value for
            padding early years.
    """
    target_end_year = (
        (args.end_year or CMIP7_SM_EXT_END_YEAR)
        if args.ext
        else CMIP7_SM_VOLCANIC_END_YEAR
    )
    hold_constant = args.ext

    if args.pad:
        save_stratospheric_aerosol_optical_depth(
            args,
            CMIP7_SM_VOLCANIC_BEG_YEAR,
            CMIP7_SM_VOLCANIC_END_YEAR,
            dataset_path,
            esm_sm_forcing_save_dirpath(args),
            pi_mean_saod=pi_mean_saod,
            save_end_year=target_end_year,
            hold_constant=hold_constant,
        )
    else:
        save_stratospheric_aerosol_optical_depth(
            args,
            CMIP7_SM_VOLCANIC_BEG_YEAR,
            CMIP7_SM_VOLCANIC_END_YEAR,
            dataset_path,
            esm_sm_forcing_save_dirpath(args),
            pi_mean_saod=pi_mean_saod,
            save_beg_year=CMIP7_SM_VOLCANIC_BEG_YEAR,
            save_end_year=target_end_year,
            hold_constant=hold_constant,
        )


if __name__ == "__main__":
    args = parse_args()

    pi_config = DatasetConfig.from_yaml(args.config, section="pi")
    sm_config = DatasetConfig.from_yaml(args.config, section="sm")
    pi_dataset = pi_config.to_dataset()
    sm_dataset = sm_config.to_dataset()

    # Calculate the pre-industrial average stratospheric optical depth.
    pi_mean_saod = (
        average_stratospheric_aerosol_optical_depth(pi_dataset) * SAOD_SCALING
    )
    # Calculate and save the average stratospheric aerosol optical depth.
    save_sm_stratospheric_aerosol_optical_depth(
        args, sm_dataset, pi_mean_saod=pi_mean_saod
    )
