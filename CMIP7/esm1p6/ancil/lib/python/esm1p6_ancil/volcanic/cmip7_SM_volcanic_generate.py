'''
Generate the CMIP7 ScenarioMIP volcanic ancillary file.
This script generates the CMIP7 ScenarioMIP volcanic ancillary file by calculating the average stratospheric aerosol optical depth (SAOD) for each historical month. 
The SAOD is calculated by averaging extinction over latitude and summing over stratospheric layers. 
The resulting SAOD is saved to the specified save file.
The script takes command line arguments for the dataset version, dataset date range, and save filename.
The generated file is saved in the specified directory path.
'''
from argparse import ArgumentParser

from cmip7_ancil_argparse import dataset_parser, path_parser
from cmip7_SM import esm_sm_forcing_save_dirpath
from volcanic.cmip7_PI_volcanic_generate import (
    average_stratospheric_aerosol_optical_depth,
    cmip7_pi_volcanic_filename,
)
from volcanic.cmip7_volcanic import (
    SAOD_SCALING,
    cmip7_volcanic_dirpath,
    save_stratospheric_aerosol_optical_depth,
)

# TODO: Are these the same as in cmip7_SM.py? If so, we should use those instead of duplicating the values here.
CMIP7_SM_VOLCANIC_BEG_YEAR = 2022
CMIP7_SM_VOLCANIC_END_YEAR = 2100


def parse_args():
    '''
    Parse the command line arguments for CMIP7 ScenarioMIP volcanic ancil file generation.
    '''
    parser = ArgumentParser(
        prog="cmip7_SM_volcanic_generate",
        description=(
            "Generate input files from CMIP7 ScenarioMIP volcanic forcings"
        ),
        parents=[path_parser(), dataset_parser()],
    )
    parser.add_argument("--pi-dataset-version")
    parser.add_argument("--pi-dataset-vdate")
    parser.add_argument("--pi-dataset-date-range")
    parser.add_argument("--scenario")
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    # --dataset-version and --dataset-vdate are already included in the dataset_parser() parent parser.
    return parser.parse_args()


def cmip7_sm_volcanic_filename(dataset_version, dataset_date_range):
    '''
    Return the filename for the CMIP7 ScenarioMIP volcanic ancil file.
    '''
    return (
        f"ext_input4MIPs_aerosolProperties_ScenarioMIP_"
        f"{dataset_version}_gnz_"
        f"{dataset_date_range}.nc"
    )

#  TODO: Is this function really needed?
def save_sm_stratospheric_aerosol_optical_depth(args, dataset_path, pi_mean_saod):
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
        pi_mean_saod=pi_mean_saod,
    )


if __name__ == "__main__":
    '''
    Generate the CMIP7 ScenarioMIP volcanic ancillary file.
    '''
    args = parse_args()

    pi_dirpath = cmip7_volcanic_dirpath(
        args, "CMIP", "monC", args.pi_dataset_version, args.pi_dataset_vdate,
    )
    pi_filename = cmip7_pi_volcanic_filename(
        args.pi_dataset_version, args.pi_dataset_date_range,
    )
    pi_dataset_path = pi_dirpath / pi_filename

    sm_dirpath = cmip7_volcanic_dirpath(
        args, "ScenarioMIP", "mon", args.dataset_version, args.dataset_vdate,
    )
    sm_filename = cmip7_sm_volcanic_filename(
        args.dataset_version, args.dataset_date_range,
    )
    sm_dataset_path = sm_dirpath / sm_filename

    # Calculate the pre-industrial average stratospheric optical depth.
    pi_mean_saod = average_stratospheric_aerosol_optical_depth(
        pi_dataset_path
    ) * SAOD_SCALING

    # Calculate and save the average stratospheric aerosol optical depth.
    save_sm_stratospheric_aerosol_optical_depth(
        args,
        sm_dataset_path,
        pi_mean_saod=pi_mean_saod)
