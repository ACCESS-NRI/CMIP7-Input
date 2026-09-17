"""Shared helpers for ACCESS-ESM1.6 volcanic historical generators."""

from __future__ import annotations

<<<<<<< HEAD
from cmip7_inputs.models.access_esm1p6.generators._common_HI import esm_hi_forcing_save_dirpath

from cmip7_inputs.models.access_esm1p6.generators.volcanic._common import save_stratospheric_aerosol_optical_depth


# TODO: Are these the same as the cmip7_HI_BEG_YEAR and cmip7_HI_END_YEAR? If so, we should use those instead of duplicating the values here.
CMIP7_HI_VOLCANIC_BEG_YEAR = 1850
CMIP7_HI_VOLCANIC_END_YEAR = 2023


def cmip7_hi_volcanic_filename(dataset_version, dataset_date_range):
=======
from cmip7_inputs.models.access_esm1p6.generators._common_historical import get_historical_save_dirpath

from cmip7_inputs.models.access_esm1p6.generators.volcanic._common import save_stratospheric_aerosol_optical_depth

from cmip7_inputs.models.access_esm1p6.generators._constants import (
    HI_VOLCANIC_START_YEAR,
    HI_VOLCANIC_END_YEAR,
)


def get_hi_volcanic_filename(dataset_version, dataset_date_range):
>>>>>>> 846bfef (Add volcanic before testing)
    '''
    Return the filename for the CMIP7 historical volcanic ancil file.
    '''
    return (
        f"ext_input4MIPs_aerosolProperties_CMIP_"
        f"{dataset_version}_gnz_"
        f"{dataset_date_range}.nc"
    )

#  TODO: Is this function really needed?
<<<<<<< HEAD
def save_hi_stratospheric_aerosol_optical_depth(args, dataset_path):
=======
def save_hi_stratospheric_aerosol_optical_depth(ancil_target_dirname,args, dataset_path):
>>>>>>> 846bfef (Add volcanic before testing)
    """
    Calculate the average stratospheric aerosol optical depth (SAOD)
    for each historical month by averaging extinction over latitude,
    and summing over stratospheric layers. Save to the save file.
    """
    save_stratospheric_aerosol_optical_depth(
        args,
<<<<<<< HEAD
        CMIP7_HI_VOLCANIC_BEG_YEAR,
        CMIP7_HI_VOLCANIC_END_YEAR,
        dataset_path,
        esm_hi_forcing_save_dirpath(args),
=======
        HI_VOLCANIC_START_YEAR,
        HI_VOLCANIC_END_YEAR,
        dataset_path,
        get_historical_save_dirpath(ancil_target_dirname),
>>>>>>> 846bfef (Add volcanic before testing)
    )
