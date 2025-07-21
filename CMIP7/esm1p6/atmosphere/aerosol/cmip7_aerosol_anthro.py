from aerosol.cmip7_aerosol_common import zero_poles

from cmip7_ancil_common import (
        esm_grid_mask,
        fix_coords,
        interpolation_scheme,
        save_ancil)
from cmip7_ancil_paths import CMIP7_SOURCE_DATA

from iris.util import equalise_attributes
from pathlib import Path

import iris
import os


CMIP7_AEROSOL_ANTHRO_VERSION = os.environ[
        'CMIP7_AEROSOL_ANTHRO_VERSION']
CMIP7_AEROSOL_ANTHRO_VDATE = os.environ[
        'CMIP7_AEROSOL_ANTHRO_VDATE']


def cmip7_aerosol_anthro_base(version):
    return Path(CMIP7_SOURCE_DATA) / 'PNNL-JGCRI' / version / 'atmos' / 'mon'


def cmip7_aerosol_anthro_pathname(species, version, vdate, date_range):
    base = cmip7_aerosol_anthro_base(version)
    filename = (
        f'{species}-em-anthro_input4MIPs_emissions_'
        f'CMIP_{version}_gn_{date_range}.nc')
    return str(base / f'{species}_em_anthro' / 'gn' / vdate / filename)


def cmip7_aerosol_anthro_pathname_list(
        species,
        version,
        vdate,
        date_range_list):
    return [cmip7_aerosol_anthro_pathname(species, version, vdate, date_range)
            for date_range in date_range_list]


def load_cmip7_aerosol_anthro(
        species,
        version,
        vdate,
        date_range,
        constraint):
    pathname = cmip7_aerosol_anthro_pathname(
            species,
            version,
            vdate,
            date_range)
    cube = iris.load_cube(
            pathname,
            constraint)
    fix_coords(cube)
    return cube


def load_cmip7_aerosol_anthro_list(
        species,
        version,
        vdate,
        date_range_list,
        constraint):
    pathname_list = cmip7_aerosol_anthro_pathname_list(
            species,
            version,
            vdate,
            date_range_list)
    cube_list = iris.load_raw(
            pathname_list,
            constraint)
    equalise_attributes(cube_list)
    cube = cube_list.concatenate_cube()
    fix_coords(cube)
    return cube


def cmip7_aerosol_anthro_interpolate(
        load_fn,
        species,
        stash_item,
        save_dir,
        ancil_filename):
    cube = load_fn(species)
    cube_tot = cube.collapsed(['sector'], iris.analysis.SUM)
    esm_cube = cube_tot.regrid(esm_grid_mask, interpolation_scheme)
    esm_cube.data = esm_cube.data.filled(0.0)
    zero_poles(esm_cube)
    esm_cube.attributes['STASH'] = iris.fileformats.pp.STASH(
        model=1,
        section=0,
        item=stash_item)
    save_ancil(esm_cube, save_dir, ancil_filename)
