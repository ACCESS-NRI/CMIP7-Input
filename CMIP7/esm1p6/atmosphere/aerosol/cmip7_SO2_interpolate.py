# Interpolate CMIP7 PI SO2 emissions to ESM1-6 grid

from cmip7_ancil_common import (
        esm_grid_mask,
        interpolation_scheme,
        join_pathname,
        save_ancil)
from aerosol.cmip7_aerosol_common import zero_poles
from aerosol.cmip7_aerosol_anthro import (
        cmip7_aerosol_anthro_pathname,
        CMIP7_AEROSOL_ANTHRO_VDATE,
        CMIP7_AEROSOL_ANTHRO_VERSION)

import iris
import netCDF4
import tempfile


DMS_NAME_CONSTRAINT = iris.Constraint(
        name='tendency_of_atmosphere_mass_content_of_'
             'dimethyl_sulfide_expressed_as_sulfur_due_to_emission')


def load_sector_dict(date_range_maybe_list):
    date_range = (
            date_range_maybe_list[0]
            if isinstance(date_range_maybe_list, list)
            else
            date_range_maybe_list)
    # Iris doesn't read the sector coordinate so use netCDF4
    d = netCDF4.Dataset(cmip7_aerosol_anthro_pathname(
            'SO2',
            CMIP7_AEROSOL_ANTHRO_VERSION,
            CMIP7_AEROSOL_ANTHRO_VDATE,
            date_range))
    sectord = dict()
    for s in d['sector'].ids.split(';'):
        i, name = s.split(':')
        sectord[name.strip()] = int(i)
    d.close()
    return sectord


def load_dms(
        dms_ancil_dirname,
        dms_ancil_filename,
        fix_ancil_date_fn):
    # Use the CMIP6 DMS
    dms_ancil_pathname = join_pathname(
            dms_ancil_dirname,
            dms_ancil_filename)

    with tempfile.TemporaryDirectory() as temp:
        dms_ancil_tempname = join_pathname(
                temp,
                dms_ancil_filename)
        # Create a temporary file with fixed dates
        # from the CMIP6 DMS file
        fix_ancil_date_fn(
                ifile=dms_ancil_pathname,
                ofile=dms_ancil_tempname)
        dms = iris.load_cube(
                dms_ancil_tempname,
                DMS_NAME_CONSTRAINT)
        # Force load since temp is temporary
        _ = dms.data
        return dms


def match_time_attributes(from_cube, to_cube):
    # Make the time attributes and coordinates match
    from_time = from_cube.coord('time')
    to_time = to_cube.coord('time')
    to_time.units = from_time.units
    to_time.points = from_time.points
    to_time.bounds = from_time.bounds
    to_time.long_name = from_time.long_name
    to_time.var_name = from_time.var_name
    for attr, value in from_time.attributes.items():
        to_time.attributes[attr] = value


def save_cmip7_so2_aerosol_anthro(
        cmip7_load_fn,
        date_range,
        dms_load_fn,
        ancil_dirname,
        ancil_filename):

    cmip7_so2 = cmip7_load_fn('SO2')

    # Iris doesn't read the sector coordinate
    sectord = load_sector_dict(date_range)

    cmip7_so2_high = (
            cmip7_so2[:, sectord['Energy']]
            + 0.5 * cmip7_so2[:, sectord['Industrial']])
    cmip7_so2_tot = cmip7_so2.collapsed(['sector'], iris.analysis.SUM)
    cmip7_so2_low = cmip7_so2_tot - cmip7_so2_high

    # For ESM1.6, factor of 0.5 to go to mass of S
    so2_low = 0.5 * cmip7_so2_low.regrid(
            esm_grid_mask,
            interpolation_scheme)
    so2_high = 0.5 * cmip7_so2_high.regrid(
            esm_grid_mask,
            interpolation_scheme)

    so2_low.data = so2_low.data.filled(0.0)
    so2_high.data = so2_high.data.filled(0.0)

    zero_poles(so2_low)
    zero_poles(so2_high)

    so2_low.attributes['STASH'] = iris.fileformats.pp.STASH(
            model=1,
            section=0,
            item=58)
    so2_high.attributes['STASH'] = iris.fileformats.pp.STASH(
            model=1,
            section=0,
            item=126)

    # Need to remove the sector coordinate before saving
    # because high doesn't have it
    so2_low.remove_coord('sector')

    # Use the CMIP6 DMS
    dms = dms_load_fn()

    # Make the attributes and coordinates match
    match_time_attributes(so2_low, dms)

    save_ancil(
            [so2_low, so2_high, dms],
            ancil_dirname,
            ancil_filename)
