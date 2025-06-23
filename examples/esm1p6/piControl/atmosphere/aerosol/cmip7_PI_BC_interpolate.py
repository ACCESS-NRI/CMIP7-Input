# Interpolate CMIP7 PI BC emissions to ESM1-6 grid
from cmip7_PI_aerosol_common import *

bc_cmip7 = load_cmip7_1850_aerosol('BC')

bc_tot_cmip7 = bc_cmip7.collapsed(['sector'], iris.analysis.SUM)

bc_esm16 = bc_tot_cmip7.regrid(mask_esm15,interpolation_scheme)

bc_esm16.data = bc_esm16.data.filled(0.)

zero_poles(bc_esm16)

bc_esm16.attributes['STASH'] = iris.fileformats.pp.STASH(model=1, section=0, item=129)

save_ancil(bc_esm16, '/g/data/tm70/mrd599/esm16_aerosols/BC_1850_cmip7.anc')
