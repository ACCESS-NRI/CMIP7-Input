import warnings
from argparse import ArgumentParser

from cmip7_ancil_argparse import (
    dataset_parser,
    ext_parser,
    pad_parser,
    path_parser,
)
from cmip7_SM import CMIP7_SM_EXT_END_YEAR, esm_sm_forcing_save_dirpath
from volcanic.cmip7_PI_volcanic_generate import (
    average_stratospheric_aerosol_optical_depth,
    cmip7_pi_volcanic_filename,
)
from volcanic.cmip7_volcanic import (
    SAOD_SCALING,
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
        parents=[
            dataset_parser(),
            pad_parser(),
            path_parser(),
            ext_parser(),
        ],
    )
    parser.add_argument("--pi-dataset-version")
    parser.add_argument("--pi-dataset-vdate")
    parser.add_argument("--pi-dataset-date-range")
    parser.add_argument("--scenario")
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_sm_volcanic_filename(dataset_version, dataset_date_range):
    return (
        f"ext_input4MIPs_aerosolProperties_ScenarioMIP_"
        f"{dataset_version}_gnz_"
        f"{dataset_date_range}.nc"
    )


def save_sm_stratospheric_aerosol_optical_depth(
    args, dataset_path, pi_mean_saod
):
    """
    Calculate the average stratospheric aerosol optical depth (SAOD)
    for each historical month by averaging extinction over latitude,
    and summing over stratospheric layers. Save to the save file.
    """
    is_ext = getattr(args, "ext", False)
    target_end_year = (
        (getattr(args, "end_year", None) or CMIP7_SM_EXT_END_YEAR)
        if is_ext
        else CMIP7_SM_VOLCANIC_END_YEAR
    )
    hold_constant = is_ext

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

    sm_dirpath = cmip7_volcanic_dirpath(
        args,
        "ScenarioMIP",
        "mon",
        args.dataset_version,
        args.dataset_vdate,
    )
    sm_filename = cmip7_sm_volcanic_filename(
        args.dataset_version,
        args.dataset_date_range,
    )
    sm_dataset_path = sm_dirpath / sm_filename

    if not sm_dataset_path.exists():
        warnings.warn(
            f"ScenarioMIP volcanic dataset {sm_dataset_path} not found.",
            UserWarning,
        )
    else:
        pi_dirpath = cmip7_volcanic_dirpath(
            args,
            "CMIP",
            "monC",
            args.pi_dataset_version,
            args.pi_dataset_vdate,
        )
        pi_filename = cmip7_pi_volcanic_filename(
            args.pi_dataset_version,
            args.pi_dataset_date_range,
        )
        pi_dataset_path = pi_dirpath / pi_filename

        # Calculate the pre-industrial average stratospheric optical depth.
        pi_mean_saod = (
            average_stratospheric_aerosol_optical_depth(pi_dataset_path)
            * SAOD_SCALING
        )
        # Calculate and save the average stratospheric aerosol optical depth.
        save_sm_stratospheric_aerosol_optical_depth(
            args, sm_dataset_path, pi_mean_saod=pi_mean_saod
        )
