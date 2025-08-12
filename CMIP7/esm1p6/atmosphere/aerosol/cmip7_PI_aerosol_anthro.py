from aerosol.cmip7_aerosol_anthro import (
        cmip7_aerosol_anthro_interpolate,
        CMIP7_AEROSOL_ANTHRO_VERSION,
        CMIP7_AEROSOL_ANTHRO_VDATE,
        load_cmip7_aerosol_anthro)
from aerosol.cmip7_PI_aerosol import ESM_PI_AEROSOL_SAVE_DIR

from cmip7_PI import CMIP7_PI_DATE_CONSTRAINT

import os


CMIP7_PI_AEROSOL_ANTHRO_DATE_RANGE = os.environ[
        'CMIP7_PI_AEROSOL_ANTHRO_DATE_RANGE']


def load_cmip7_pi_aerosol_anthro(species):
    return load_cmip7_aerosol_anthro(
            species,
            CMIP7_AEROSOL_ANTHRO_VERSION,
            CMIP7_AEROSOL_ANTHRO_VDATE,
            CMIP7_PI_AEROSOL_ANTHRO_DATE_RANGE,
            CMIP7_PI_DATE_CONSTRAINT)


def cmip7_pi_aerosol_anthro_interpolate(species, stash_item, ancil_filename):
    cmip7_aerosol_anthro_interpolate(
            load_cmip7_pi_aerosol_anthro,
            species,
            stash_item,
            ESM_PI_AEROSOL_SAVE_DIR,
            ancil_filename)
