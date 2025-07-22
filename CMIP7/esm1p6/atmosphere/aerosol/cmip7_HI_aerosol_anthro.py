from aerosol.cmip7_aerosol_anthro import (
        cmip7_aerosol_anthro_interpolate,
        CMIP7_AEROSOL_ANTHRO_VERSION,
        CMIP7_AEROSOL_ANTHRO_VDATE,
        load_cmip7_aerosol_anthro_list)
from aerosol.cmip7_HI_aerosol import ESM_HI_AEROSOL_SAVE_DIR

from cmip7_HI import CMIP7_HI_DATE_CONSTRAINT

import os


CMIP7_HI_AEROSOL_ANTHRO_DATE_RANGE_LIST = eval(os.environ[
        'CMIP7_HI_AEROSOL_ANTHRO_DATE_RANGE_LIST'])


def load_cmip7_hi_aerosol_anthro(species):
    return load_cmip7_aerosol_anthro_list(
            species,
            CMIP7_AEROSOL_ANTHRO_VERSION,
            CMIP7_AEROSOL_ANTHRO_VDATE,
            CMIP7_HI_AEROSOL_ANTHRO_DATE_RANGE_LIST,
            CMIP7_HI_DATE_CONSTRAINT)


def cmip7_hi_aerosol_anthro_interpolate(species, stash_item, ancil_filename):
    cmip7_aerosol_anthro_interpolate(
            load_cmip7_hi_aerosol_anthro,
            species,
            stash_item,
            ESM_HI_AEROSOL_SAVE_DIR,
            ancil_filename)
