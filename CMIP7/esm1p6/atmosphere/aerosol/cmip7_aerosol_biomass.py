from aerosol.cmip7_aerosol_common import zero_poles

from cmip7_ancil_common import (
        esm_grid_mask,
        interpolation_scheme,
        save_ancil,
        set_coord_system)
from cmip7_ancil_paths import CMIP7_SOURCE_DATA

from datetime import datetime
from iris.util import equalise_attributes
from pathlib import Path

import concurrent.futures as cf
import iris
import os

CMIP7_AEROSOL_BIOMASS_VERSION = os.environ[
        'CMIP7_AEROSOL_BIOMASS_VERSION']
CMIP7_AEROSOL_BIOMASS_VDATE = os.environ[
        'CMIP7_AEROSOL_BIOMASS_VDATE']
CMIP7_AEROSOL_BIOMASS_PERCENTAGE_DATE_RANGE = os.environ[
        'CMIP7_AEROSOL_BIOMASS_PERCENTAGE_DATE_RANGE']


def cmip7_aerosol_biomass_base(version):
    return Path(CMIP7_SOURCE_DATA) / 'DRES' / version / 'atmos' / 'mon'


def cmip7_aerosol_biomass_pathname(species, version, vdate, date_range):
    base = cmip7_aerosol_biomass_base(version)
    filename = (
        f'{species}_input4MIPs_emissions_'
        f'CMIP_{version}_gn_{date_range}.nc')
    return str(base / species / 'gn' / vdate / filename)


def cmip7_aerosol_biomass_pathname_list(
        species,
        version,
        vdate,
        date_range_list):
    return [cmip7_aerosol_biomass_pathname(
            species,
            version,
            vdate,
            date_range)
            for date_range in date_range_list]


def load_cmip7_aerosol_biomass(
        species,
        version,
        vdate,
        date_range,
        constraint):
    pathname = cmip7_aerosol_biomass_pathname(
            species,
            version,
            vdate,
            date_range)
    cube = iris.load_cube(
            pathname,
            constraint)
    return cube


def load_cmip7_aerosol_biomass_list(
        species,
        version,
        vdate,
        date_range_list,
        constraint):
    pathname_list = cmip7_aerosol_biomass_pathname_list(
            species,
            version,
            vdate,
            date_range_list),
    cube_list = iris.load_raw(
            pathname_list,
            constraint)
    equalise_attributes(cube_list)
    cube = cube_list.concatenate_cube()
    return cube


force_load = True


def split_frac_low_high(
        load_pc_fn,
        species):
    sources = ['AGRI', 'BORF', 'DEFO', 'PEAT', 'SAVA', 'TEMF']
    pc = dict()
    futures = dict()
    with cf.ProcessPoolExecutor(max_workers=len(sources)) as ex:
        for source in sources:
            futures[source] = ex.submit(
                    load_pc_fn,
                    f'{species}percentage{source}')
            pc[source] = futures[source].result()
    # For the low/high split follow Met Office CMIP6
    # low: AGRI, PEAT, SAVA
    # high: BORF, DEFO, TEMF
    frac_low = (
        0.01 * (pc['AGRI'] + pc['PEAT'] + pc['SAVA']))
    frac_high = (
        0.01 * (pc['BORF'] + pc['DEFO'] + pc['TEMF']))
    if force_load:
        _ = frac_low.data
        now = datetime.now()
        print(f'{now}: Realised bb {species} low')
        _ = frac_high.data
        now = datetime.now()
        print(f'{now}: Realised bb {species} high')
    return frac_low, frac_high


def save_cmip7_aerosol_biomass(
        load_pc_fn,
        load_fn,
        ancil_dirname,
        ancil_filename):
    bc_frac_low, bc_frac_high = split_frac_low_high(
            load_pc_fn,
            'BC')
    oc_frac_low, oc_frac_high = split_frac_low_high(
            load_pc_fn,
            'OC')

    bc = load_fn('BC')
    oc = load_fn('OC')

    low = bc * bc_frac_low + oc * oc_frac_low
    high = bc * bc_frac_high + oc * oc_frac_high

    if force_load:
        _ = low.data
        _ = high.data
        now = datetime.now()
        print(f'{now}: LO, HI done')

    # Regrid requires matching coordinate systems
    set_coord_system(low)
    set_coord_system(high)

    now = datetime.now()
    print(f'{now}: set_coord_system done')

    # This data is missing over oceans,
    # so needs to be filled with zero for the model
    low.data = low.data.filled(0.0)
    high.data = high.data.filled(0.0)

    now = datetime.now()
    print(f'{now}: filled done')

    low_esm = low.regrid(esm_grid_mask, interpolation_scheme)
    high_esm = high.regrid(esm_grid_mask, interpolation_scheme)

    now = datetime.now()
    print(f'{now}: regrid done')

    zero_poles(low_esm)
    zero_poles(high_esm)

    now = datetime.now()
    print(f'{now}: zero_poles done')

    low_esm.attributes['STASH'] = iris.fileformats.pp.STASH(
            model=1,
            section=0,
            item=130)
    high_esm.attributes['STASH'] = iris.fileformats.pp.STASH(
            model=1,
            section=0,
            item=131)

    save_ancil(
            [low_esm, high_esm],
            ancil_dirname,
            ancil_filename)

    now = datetime.now()
    print(f'{now}: save_ancil done')
