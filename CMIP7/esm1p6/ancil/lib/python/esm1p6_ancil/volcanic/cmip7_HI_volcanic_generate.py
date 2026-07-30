from argparse import ArgumentParser

from cmip7_ancil_argparse import dataset_parser, path_parser
from cmip7_HI import esm_hi_forcing_save_dirpath
from volcanic.cmip7_volcanic import (
    cmip7_volcanic_dirpath,
    save_stratospheric_aerosol_optical_depth,
)

# TODO: Are these the same as the cmip7_HI_BEG_YEAR and cmip7_HI_END_YEAR? If so, we should use those instead of duplicating the values here.
CMIP7_HI_VOLCANIC_BEG_YEAR = 1850
CMIP7_HI_VOLCANIC_END_YEAR = 2023


def parse_args():
    '''
    Parse the command line arguments for CMIP7 historical volcanic ancil file generation.
    '''
    parser = ArgumentParser(
        prog="cmip7_HI_volcanic_generate",
        description=(
            "Generate input files from CMIP7 historical volcanic forcings"
        ),
        parents=[path_parser(), dataset_parser()],
    )
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_hi_volcanic_filename(dataset_version, dataset_date_range):
    '''
    Return the filename for the CMIP7 historical volcanic ancil file.
    '''
    return (
        f"ext_input4MIPs_aerosolProperties_CMIP_"
        f"{dataset_version}_gnz_"
        f"{dataset_date_range}.nc"
    )

#  TODO: Is this function really needed?
def save_hi_stratospheric_aerosol_optical_depth(args, dataset_path):
    """
    Calculate the average stratospheric aerosol optical depth (SAOD)
    for each historical month by averaging extinction over latitude,
    and summing over stratospheric layers. Save to the save file.
    """
    save_stratospheric_aerosol_optical_depth(
        args,
        CMIP7_HI_VOLCANIC_BEG_YEAR,
        CMIP7_HI_VOLCANIC_END_YEAR,
        dataset_path,
        esm_hi_forcing_save_dirpath(args),
    )


if __name__ == "__main__":
    '''
    Generate the CMIP7 historical volcanic ancillary file.
    '''
    args = parse_args()

    dirpath = cmip7_volcanic_dirpath(
        args, "CMIP", "mon", args.dataset_version, args.dataset_vdate,
    )
    filename = cmip7_hi_volcanic_filename(
        args.dataset_version, args.dataset_date_range,
    )
    dataset_path = dirpath / filename

    # Calculate and save the average stratospheric aerosol optical depth.
    save_hi_stratospheric_aerosol_optical_depth(args, dataset_path)
