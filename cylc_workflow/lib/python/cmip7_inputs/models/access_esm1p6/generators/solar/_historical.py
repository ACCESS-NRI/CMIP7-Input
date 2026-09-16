"""Helpers for solar historical"""

from __future__ import annotations

from cmip7_inputs.models.access_esm1p6.generators._common_historical import get_historical_save_dirpath

from cmip7_inputs.models.access_esm1p6.generators.solar._common import save_solar

from cmip7_inputs.models.access_esm1p6.generators._constants import (
    HI_START_YEAR,
    HI_END_YEAR
)

def save_historical_solar(ancil_target_dirname, args, cube):
    """
    Save the Total Solar Irradiance values for each year into a text file.
    """
    save_dirpath = get_historical_save_dirpath(ancil_target_dirname)
    save_solar(
        args, cube, HI_START_YEAR, HI_END_YEAR, save_dirpath
    )