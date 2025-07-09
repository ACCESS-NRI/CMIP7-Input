from cmip7_ancil_common import CMIP7_PI_DATE_CONSTRAINT
from cmip7_ancil_paths import CMIP7_SOURCE_DATA

from pathlib import Path

import iris
import os

CMIP7_AEROSOL_BIOMASS_VERSION = os.environ[
        'CMIP7_AEROSOL_BIOMASS_VERSION']
CMIP7_AEROSOL_BIOMASS_VDATE = os.environ[
        'CMIP7_AEROSOL_BIOMASS_VDATE']
CMIP7_AEROSOL_BIOMASS_DATE_RANGE = os.environ[
        'CMIP7_AEROSOL_BIOMASS_DATE_RANGE']
CMIP7_AEROSOL_BIOMASS_PERCENTAGE_DATE_RANGE = os.environ[
        'CMIP7_AEROSOL_BIOMASS_PERCENTAGE_DATE_RANGE']


def cmip7_aerosol_biomass_base(version):
    return Path(CMIP7_SOURCE_DATA) / 'DRES' / version / 'atmos' / 'mon'


def cmip7_aerosol_biomass_pathname(species, version, vdate, date_range):
    base = cmip7_aerosol_biomass_base(version)
    filename = (
        f'{species}_input4MIPs_emissions_CMIP_{version}_gn_{date_range}.nc')
    return str(base / species / 'gn' / vdate / filename)


def load_cmip7_aerosol_biomass(
        species,
        version,
        vdate,
        date_range,
        constraint):
    return iris.load_cube(
            cmip7_aerosol_biomass_pathname(
                species,
                version,
                vdate,
                date_range),
            constraint)


def load_cmip7_pi_aerosol_biomass(species):
    return load_cmip7_aerosol_biomass(
            species,
            CMIP7_AEROSOL_BIOMASS_VERSION,
            CMIP7_AEROSOL_BIOMASS_VDATE,
            CMIP7_AEROSOL_BIOMASS_DATE_RANGE,
            CMIP7_PI_DATE_CONSTRAINT)


def load_cmip7_pi_aerosol_biomass_percentage(species):
    return load_cmip7_aerosol_biomass(
            species,
            CMIP7_AEROSOL_BIOMASS_VERSION,
            CMIP7_AEROSOL_BIOMASS_VDATE,
            CMIP7_AEROSOL_BIOMASS_PERCENTAGE_DATE_RANGE,
            CMIP7_PI_DATE_CONSTRAINT)
