from aerosol.cmip7_aerosol_biomass import (
        CMIP7_AEROSOL_BIOMASS_PERCENTAGE_DATE_RANGE,
        CMIP7_AEROSOL_BIOMASS_VERSION,
        CMIP7_AEROSOL_BIOMASS_VDATE,
        load_cmip7_aerosol_biomass)

from cmip7_PI import CMIP7_PI_DATE_CONSTRAINT

import os


CMIP7_PI_AEROSOL_BIOMASS_DATE_RANGE = os.environ[
        'CMIP7_PI_AEROSOL_BIOMASS_DATE_RANGE']


def load_cmip7_pi_aerosol_biomass(species):
    return load_cmip7_aerosol_biomass(
            species,
            CMIP7_AEROSOL_BIOMASS_VERSION,
            CMIP7_AEROSOL_BIOMASS_VDATE,
            CMIP7_PI_AEROSOL_BIOMASS_DATE_RANGE,
            CMIP7_PI_DATE_CONSTRAINT)


def load_cmip7_pi_aerosol_biomass_percentage(species):
    return load_cmip7_aerosol_biomass(
            species,
            CMIP7_AEROSOL_BIOMASS_VERSION,
            CMIP7_AEROSOL_BIOMASS_VDATE,
            CMIP7_AEROSOL_BIOMASS_PERCENTAGE_DATE_RANGE,
            CMIP7_PI_DATE_CONSTRAINT)
