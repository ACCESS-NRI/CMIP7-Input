from aerosol.cmip7_aerosol_biomass import (
        CMIP7_AEROSOL_BIOMASS_PERCENTAGE_DATE_RANGE,
        CMIP7_AEROSOL_BIOMASS_VERSION,
        CMIP7_AEROSOL_BIOMASS_VDATE,
        load_cmip7_aerosol_biomass,
        load_cmip7_aerosol_biomass_list)

from cmip7_HI import CMIP7_HI_DATE_CONSTRAINT

import os


CMIP7_HI_AEROSOL_BIOMASS_DATE_RANGE_LIST = eval(os.environ[
        'CMIP7_HI_AEROSOL_BIOMASS_DATE_RANGE_LIST'])


def load_cmip7_hi_aerosol_biomass(species):
    return load_cmip7_aerosol_biomass_list(
            species,
            CMIP7_AEROSOL_BIOMASS_VERSION,
            CMIP7_AEROSOL_BIOMASS_VDATE,
            CMIP7_HI_AEROSOL_BIOMASS_DATE_RANGE_LIST,
            CMIP7_HI_DATE_CONSTRAINT)


def load_cmip7_hi_aerosol_biomass_percentage(species):
    return load_cmip7_aerosol_biomass(
            species,
            CMIP7_AEROSOL_BIOMASS_VERSION,
            CMIP7_AEROSOL_BIOMASS_VDATE,
            CMIP7_AEROSOL_BIOMASS_PERCENTAGE_DATE_RANGE,
            CMIP7_HI_DATE_CONSTRAINT)
