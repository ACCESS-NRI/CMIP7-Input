from argparse import ArgumentParser

from cmip7_ancil_argparse import (
    config_parser,
    pad_parser,
    path_parser,
)
from cmip7_HI import esm_hi_forcing_save_dirpath
from dataset import DatasetConfig
from volcanic.cmip7_volcanic import save_stratospheric_aerosol_optical_depth

CMIP7_HI_VOLCANIC_BEG_YEAR = 1850
CMIP7_HI_VOLCANIC_END_YEAR = 2023


def parse_args():
    """Parse command-line arguments for historical volcanic forcing generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing dataset config, pad,
            path, and save filename parameters.
    """
    parser = ArgumentParser(
        prog="cmip7_HI_volcanic_generate",
        description=(
            "Generate input files from CMIP7 historical volcanic forcings"
        ),
        parents=[
            path_parser(),
            config_parser(),
            pad_parser(),
        ],
    )
    parser.add_argument("--save-filename")
    return parser.parse_args()


def save_hi_stratospheric_aerosol_optical_depth(args, dataset_path):
    """Calculate the average stratospheric aerosol optical depth (SAOD)
    for each historical month by averaging extinction over latitude,
    and summing over stratospheric layers. Save to the save file.

    Args:
        args (argparse.Namespace): Command-line arguments specifying pad and
            output options.
        dataset_path (os.PathLike): Path to the historical volcanic extinction
            netCDF file.
    """
    if args.pad:
        save_stratospheric_aerosol_optical_depth(
            args,
            CMIP7_HI_VOLCANIC_BEG_YEAR,
            CMIP7_HI_VOLCANIC_END_YEAR,
            dataset_path,
            esm_hi_forcing_save_dirpath(args),
        )
    else:
        save_stratospheric_aerosol_optical_depth(
            args,
            CMIP7_HI_VOLCANIC_BEG_YEAR,
            CMIP7_HI_VOLCANIC_END_YEAR,
            dataset_path,
            esm_hi_forcing_save_dirpath(args),
            pi_mean_saod=None,
            save_beg_year=CMIP7_HI_VOLCANIC_BEG_YEAR,
            save_end_year=CMIP7_HI_VOLCANIC_END_YEAR,
        )


if __name__ == "__main__":
    args = parse_args()

    config = DatasetConfig.from_yaml(args.config)
    dataset = config.to_dataset()

    # Calculate and save the average stratospheric aerosol optical depth.
    save_hi_stratospheric_aerosol_optical_depth(args, dataset)
