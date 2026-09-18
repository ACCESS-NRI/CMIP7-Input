"""Helpers for solar historical"""

from __future__ import annotations

from cmip7_inputs.models.access_esm1p6.generators.solar._common import save_solar

from cmip7_inputs.models.access_esm1p6.generators._constants import (
    HI_START_YEAR,
    HI_END_YEAR
)

def save_historical_solar(historical_save_dirpath, save_filename, cube):
    """
    Save the Total Solar Irradiance values for each year into a text file.
    """
    save_solar(
        save_filename, cube, HI_START_YEAR, HI_END_YEAR, historical_save_dirpath
    )