# Interpolate CMIP7 PI SO2 emissions to ESM1-6 grid
from cmip7_PI_aerosol_common import *
import netCDF4

so2_cmip7 = load_cmip7_1850_aerosol('SO2')

# Iris doesn't read the sector coordinate so use netCDF4
d = netCDF4.Dataset(cmip7_path('SO2'))
sectord = {}
for s in d['sector'].ids.split(';'):
    i, name = s.split(':')
    sectord[name.strip()] = int(i)
d.close()

so2_hi_cmip7 = so2_cmip7[:,sectord['Energy']] + 0.5*so2_cmip7[:,sectord['Industrial']]
so2_tot_cmip7 = so2_cmip7.collapsed(['sector'], iris.analysis.SUM)
so2_lo_cmip7 = so2_tot_cmip7 - so2_hi_cmip7

# For ESM1.5, factor of 0.5 to go to mass of S
so2_lo_esm16 = 0.5*so2_lo_cmip7.regrid(mask_esm15, interpolation_scheme)
so2_hi_esm16 = 0.5*so2_hi_cmip7.regrid(mask_esm15, interpolation_scheme)

so2_lo_esm16.data = so2_lo_esm16.data.filled(0.)
so2_hi_esm16.data = so2_hi_esm16.data.filled(0.)

zero_poles(so2_lo_esm16)
zero_poles(so2_hi_esm16)

so2_lo_esm16.attributes['STASH'] = iris.fileformats.pp.STASH(model=1, section=0, item=58)
so2_hi_esm16.attributes['STASH'] = iris.fileformats.pp.STASH(model=1, section=0, item=126)

# Need to remove the sector coordinate before saving because high doesn't have it
so2_lo_esm16.remove_coord('sector')

# Use the CMIP6 DMS
dms = iris.load_cube('/g/data/tm70/mrd599/esm15_aerosols/scycl_1850_ESM1_v4.anc',
                'tendency_of_atmosphere_mass_content_of_dimethyl_sulfide_expressed_as_sulfur_due_to_emission')

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

save_ancil([so2_lo_esm16, so2_hi_esm16, dms],
           '/g/data/tm70/mrd599/esm16_aerosols/scycl_1850_cmip7.anc')
