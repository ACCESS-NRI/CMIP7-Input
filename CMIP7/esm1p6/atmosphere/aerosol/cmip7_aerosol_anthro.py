from cmip7_ancil_common import (
        CMIP7_PI_DATE_CONSTRAINT,
        fix_coords,
        interpolation_scheme,
        mask_esm15,
        save_ancil)
from cmip7_ancil_paths import CMIP7_SOURCE_DATA

from aerosol.cmip7_aerosol_common import (
        ESM_PI_AEROSOL_SAVE_DIR,
        zero_poles)

from pathlib import Path

import iris
import os


CMIP7_AEROSOL_ANTHRO_VERSION = os.environ[
        'CMIP7_AEROSOL_ANTHRO_VERSION']
CMIP7_AEROSOL_ANTHRO_VDATE = os.environ[
        'CMIP7_AEROSOL_ANTHRO_VDATE']
CMIP7_AEROSOL_ANTHRO_DATE_RANGE = os.environ[
        'CMIP7_AEROSOL_ANTHRO_DATE_RANGE']


def cmip7_aerosol_anthro_base(version):
    return Path(CMIP7_SOURCE_DATA) / 'PNNL-JGCRI' / version / 'atmos' / 'mon'


def cmip7_aerosol_anthro_pathname(species, version, vdate, date_range):
    base = cmip7_aerosol_anthro_base(version)
    filename = (
        f'{species}-em-anthro_input4MIPs_emissions_'
        f'CMIP_{version}_gn_{date_range}.nc')
    return str(base / f'{species}_em_anthro' / 'gn' / vdate / filename)


def load_cmip7_aerosol_anthro(
        species,
        version,
        vdate,
        date_range,
        constraint):
    cube = iris.load_cube(
            cmip7_aerosol_anthro_pathname(
                species,
                version,
                vdate,
                date_range),
            constraint)
    fix_coords(cube)
    return cube


def load_cmip7_pi_aerosol_anthro(species):
    return load_cmip7_aerosol_anthro(
            species,
            CMIP7_AEROSOL_ANTHRO_VERSION,
            CMIP7_AEROSOL_ANTHRO_VDATE,
            CMIP7_AEROSOL_ANTHRO_DATE_RANGE,
            CMIP7_PI_DATE_CONSTRAINT)


def cmip7_aerosol_anthro_interpolate(species, stash_item, ancil_filename):
    cube = load_cmip7_pi_aerosol_anthro(species)
    cube_tot = cube.collapsed(['sector'], iris.analysis.SUM)
    esm_cube = cube_tot.regrid(mask_esm15, interpolation_scheme)
    esm_cube.data = esm_cube.data.filled(0.)
    zero_poles(esm_cube)
    esm_cube.attributes['STASH'] = iris.fileformats.pp.STASH(
        model=1,
        section=0,
        item=stash_item)
    save_ancil(esm_cube, ESM_PI_AEROSOL_SAVE_DIR, ancil_filename)
