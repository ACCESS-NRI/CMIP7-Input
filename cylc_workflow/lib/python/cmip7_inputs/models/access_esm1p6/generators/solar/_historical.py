"""Helpers for solar historical"""

from __future__ import annotations

from cmip7_inputs.models.access_esm1p6.generators._common_historical import esm_hi_forcing_save_dirpath

from cmip7_inputs.models.access_esm1p6.generators.solar._common import cmip7_solar_save

from cmip7_inputs.models.access_esm1p6.generators._constants import (
    HI_START_YEAR,
    HI_END_YEAR
)

def cmip7_hi_solar_save(ancil_target_dirname, args, cube):
    """
    Save the Total Solar Irradiance values for each year into a text file.
    """
    save_dirpath = esm_hi_forcing_save_dirpath(ancil_target_dirname)
    cmip7_solar_save(
        args, cube, HI_START_YEAR, HI_END_YEAR, save_dirpath
    )