from argparse import ArgumentParser

from cmip7_ancil_argparse import dataset_parser, path_parser
from cmip7_SM import esm_sm_forcing_save_dirpath
from volcanic.cmip7_volcanic import (
    cmip7_volcanic_dirpath,
    save_stratospheric_aerosol_optical_depth,
)

CMIP7_SM_VOLCANIC_BEG_YEAR = 2022
CMIP7_SM_VOLCANIC_END_YEAR = 2100


def parse_args():
    parser = ArgumentParser(
        prog="cmip7_SM_volcanic_generate",
        description=(
            "Generate input files from CMIP7 ScenarioMIP volcanic forcings"
        ),
        parents=[path_parser(), dataset_parser()],
    )
    parser.add_argument("--scenario")
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_sm_volcanic_filename(args):
    return (
        f"ext_input4MIPs_aerosolProperties_ScenarioMIP_"
        f"{args.dataset_version}_gnz_"
        f"{args.dataset_date_range}.nc"
    )


def save_sm_stratospheric_aerosol_optical_depth(args, dataset_path):
    """
    Calculate the average stratospheric aerosol optical depth (SAOD)
    for each historical month by averaging extinction over latitude,
    and summing over stratospheric layers. Save to the save file.
    """
    save_stratospheric_aerosol_optical_depth(
        args,
        CMIP7_SM_VOLCANIC_BEG_YEAR,
        CMIP7_SM_VOLCANIC_END_YEAR,
        dataset_path,
        esm_sm_forcing_save_dirpath(args),
    )


if __name__ == "__main__":
    args = parse_args()

    dirpath = cmip7_volcanic_dirpath(args, "ScenarioMIP", "mon")
    filename = cmip7_sm_volcanic_filename(args)
    dataset_path = dirpath / filename

    # Calculate and save the average stratospheric aerosol optical depth.
    save_sm_stratospheric_aerosol_optical_depth(args, dataset_path)
