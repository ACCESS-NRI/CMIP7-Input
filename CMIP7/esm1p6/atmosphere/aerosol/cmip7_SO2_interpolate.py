# Interpolate CMIP7 PI SO2 emissions to ESM1-6 grid

from cmip7_ancil_common import (
        interpolation_scheme,
        join_pathname,
        mask_esm15,
        save_ancil)
from aerosol.cmip7_aerosol_common import (
        ESM_PI_AEROSOL_SAVE_DIR,
        zero_poles)
from aerosol.cmip7_aerosol_anthro import (
        CMIP7_AEROSOL_ANTHRO_DATE_RANGE,
        cmip7_aerosol_anthro_pathname,
        CMIP7_AEROSOL_ANTHRO_VDATE,
        CMIP7_AEROSOL_ANTHRO_VERSION,
        load_cmip7_pi_aerosol_anthro)
from cmip7_ancil_paths import (
        ESM15_INPUTS_PATH,
        ESM15_PI_AEROSOL_VERSION,
        ESM_GRID_DIRNAME,
        ESM_PI_AEROSOL_REL_PATH)
from fix_esm15_PI_ancil_date import fix_esm15_pi_ancil_date

import iris
import netCDF4
import tempfile

so2_cmip7 = load_cmip7_pi_aerosol_anthro('SO2')

# Iris doesn't read the sector coordinate so use netCDF4
d = netCDF4.Dataset(cmip7_aerosol_anthro_pathname(
        'SO2',
        CMIP7_AEROSOL_ANTHRO_VERSION,
        CMIP7_AEROSOL_ANTHRO_VDATE,
        CMIP7_AEROSOL_ANTHRO_DATE_RANGE))
sectord = {}
for s in d['sector'].ids.split(';'):
    i, name = s.split(':')
    sectord[name.strip()] = int(i)
d.close()

so2_hi_cmip7 = (
        so2_cmip7[:, sectord['Energy']]
        + 0.5*so2_cmip7[:, sectord['Industrial']])
so2_tot_cmip7 = so2_cmip7.collapsed(['sector'], iris.analysis.SUM)
so2_lo_cmip7 = so2_tot_cmip7 - so2_hi_cmip7

# For ESM1.5, factor of 0.5 to go to mass of S
so2_lo_esm16 = 0.5*so2_lo_cmip7.regrid(mask_esm15, interpolation_scheme)
so2_hi_esm16 = 0.5*so2_hi_cmip7.regrid(mask_esm15, interpolation_scheme)

so2_lo_esm16.data = so2_lo_esm16.data.filled(0.)
so2_hi_esm16.data = so2_hi_esm16.data.filled(0.)

zero_poles(so2_lo_esm16)
zero_poles(so2_hi_esm16)

so2_lo_esm16.attributes['STASH'] = iris.fileformats.pp.STASH(
        model=1,
        section=0,
        item=58)
so2_hi_esm16.attributes['STASH'] = iris.fileformats.pp.STASH(
        model=1,
        section=0,
        item=126)

# Need to remove the sector coordinate before saving
# because high doesn't have i.t
so2_lo_esm16.remove_coord('sector')

# Use the CMIP6 DMS
ESM15_PI_DMS_ANCIL_FILENAME = 'scycl_1850_ESM1_v4.anc'
ESM15_PI_DMS_ANCIL_PATHNAME = str(
        ESM15_INPUTS_PATH
        / ESM_PI_AEROSOL_REL_PATH
        / ESM_GRID_DIRNAME
        / ESM15_PI_AEROSOL_VERSION
        / ESM15_PI_DMS_ANCIL_FILENAME)

with tempfile.TemporaryDirectory() as temp:
    # Create a temporary file with fixed dates from the CMIP6 DMS file
    ESM15_PI_DMS_ANCIL_TEMPNAME = join_pathname(
            temp,
            ESM15_PI_DMS_ANCIL_FILENAME)
    fix_esm15_pi_ancil_date(
            ifile=ESM15_PI_DMS_ANCIL_PATHNAME,
            ofile=ESM15_PI_DMS_ANCIL_TEMPNAME)
    dms = iris.load_cube(
            ESM15_PI_DMS_ANCIL_TEMPNAME,
            'tendency_of_atmosphere_mass_content_of_'
            'dimethyl_sulfide_expressed_as_sulfur_due_to_emission')

    # Make the attributes and coordinates match
    so2_time = so2_lo_esm16.coord('time')
    dms_time = dms.coord('time')
    dms_time.units = so2_time.units
    dms_time.points = so2_time.points
    dms_time.bounds = so2_time.bounds
    dms_time.long_name = so2_time.long_name
    dms_time.var_name = so2_time.var_name
    for attr, value in so2_time.attributes.items():
        dms_time.attributes[attr] = value

    save_ancil(
            [so2_lo_esm16, so2_hi_esm16, dms],
            ESM_PI_AEROSOL_SAVE_DIR,
            'scycl_1850_cmip7.anc')
