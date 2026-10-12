from argparse import ArgumentParser

from cmip7_ancil_argparse import (
    dataset_parser,
    pad_parser,
    path_parser,
)
from cmip7_HI import esm_hi_forcing_save_dirpath
from volcanic.cmip7_volcanic import (
    cmip7_volcanic_dirpath,
    save_stratospheric_aerosol_optical_depth,
)

CMIP7_HI_VOLCANIC_BEG_YEAR = 1850
CMIP7_HI_VOLCANIC_END_YEAR = 2023


def parse_args():
    """Parse command-line arguments for historical volcanic forcing generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing dataset, pad, path,
            date range, and save filename parameters.
    """
    parser = ArgumentParser(
        prog="cmip7_HI_volcanic_generate",
        description=(
            "Generate input files from CMIP7 historical volcanic forcings"
        ),
        parents=[
            dataset_parser(),
            pad_parser(),
            path_parser(),
        ],
    )
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_hi_volcanic_filename(dataset_version, dataset_date_range):
    """Construct the standard input4MIPs netCDF filename for historical
    volcanic extinction.

    Args:
        dataset_version (str): Version string of the volcanic dataset.
        dataset_date_range (str): Date range string (e.g. '185001-202312').

    Returns:
        str: NetCDF filename for monthly zonal extinction properties.
    """
    return (
        f"ext_input4MIPs_aerosolProperties_CMIP_"
        f"{dataset_version}_gnz_"
        f"{dataset_date_range}.nc"
    )


def save_hi_stratospheric_aerosol_optical_depth(args, dataset_path):
    """Calculate the average stratospheric aerosol optical depth (SAOD)
    for each historical month by averaging extinction over latitude,
    and summing over stratospheric layers. Save to the save file.

    Args:
        args (argparse.Namespace): Command-line arguments specifying pad and
            output options.
        dataset_path (pathlib.Path): Path to the historical volcanic extinction
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

    dirpath = cmip7_volcanic_dirpath(
        args,
        "CMIP",
        "mon",
        args.dataset_version,
        args.dataset_vdate,
    )
    filename = cmip7_hi_volcanic_filename(
        args.dataset_version,
        args.dataset_date_range,
    )
    dataset_path = dirpath / filename

    # Calculate and save the average stratospheric aerosol optical depth.
    save_hi_stratospheric_aerosol_optical_depth(args, dataset_path)
