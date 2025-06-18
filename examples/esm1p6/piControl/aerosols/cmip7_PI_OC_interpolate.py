# Interpolate CMIP7 PI OCFF emissions to ESM1-6 grid
from cmip7_PI_aerosol_common import *

oc_cmip7 = load_cmip7_1850_aerosol('OC')

oc_tot_cmip7 = oc_cmip7.collapsed(['sector'], iris.analysis.SUM)

oc_esm16 = oc_tot_cmip7.regrid(mask_esm15, interpolation_scheme)

oc_esm16.data = oc_esm16.data.filled(0.)

zero_poles(oc_esm16)

oc_esm16.attributes['STASH'] = iris.fileformats.pp.STASH(model=1, section=0, item=135)

save_ancil(oc_esm16, '/g/data/tm70/mrd599/esm16_aerosols/OCFF_1850_cmip7.anc')
