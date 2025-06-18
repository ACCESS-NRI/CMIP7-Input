# Interpolate CMIP7 PI Biomass burning emissions to ESM1-6 grid
from cmip7_PI_aerosol_common import *

# If the data are explicitly loaded
# real    1m47.602s
# user    1m30.652s
# sys     0m15.503s
# Otherwise > 20 minutes

force_load = True

def cmip7_bb_path(var):
    base = Path('/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/DRES/DRES-CMIP-BB4CMIP7-2-0/atmos/mon')
    return base / f'{var}/gn/v20250227/{var}_input4MIPs_emissions_CMIP_DRES-CMIP-BB4CMIP7-2-0_gn_175001-189912.nc'
def cmip7_bb_percent_path(var):
    base = Path('/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/DRES/DRES-CMIP-BB4CMIP7-2-0/atmos/mon')
    return base / f'{var}/gn/v20250227/{var}_input4MIPs_emissions_CMIP_DRES-CMIP-BB4CMIP7-2-0_gn_175001-202312.nc'

bb_bc_cmip7 = iris.load_cube(cmip7_bb_path('BC'), constraint_1850)
bb_bc_agri_cmip7 = iris.load_cube(cmip7_bb_percent_path('BCpercentageAGRI'), constraint_1850)
bb_bc_peat_cmip7 = iris.load_cube(cmip7_bb_percent_path('BCpercentagePEAT'), constraint_1850)
bb_bc_sava_cmip7 = iris.load_cube(cmip7_bb_percent_path('BCpercentageSAVA'), constraint_1850)
bb_bc_borf_cmip7 = iris.load_cube(cmip7_bb_percent_path('BCpercentageBORF'), constraint_1850)
bb_bc_defo_cmip7 = iris.load_cube(cmip7_bb_percent_path('BCpercentageDEFO'), constraint_1850)
bb_bc_temf_cmip7 = iris.load_cube(cmip7_bb_percent_path('BCpercentageTEMF'), constraint_1850)
# For the low/high split follow Met Office CMIP6
# low: AGRI, PEAT, SAVA
# high: BORF, DEFO, TEMF
bb_bc_frac_low_cmip7 = 0.01 * (bb_bc_agri_cmip7 + bb_bc_peat_cmip7 + bb_bc_sava_cmip7)
bb_bc_frac_high_cmip7 = 0.01 * (bb_bc_borf_cmip7 + bb_bc_defo_cmip7 + bb_bc_temf_cmip7)
if force_load:
    _ = bb_bc_frac_low_cmip7.data
    print('Realised bb_bc low')
    _ = bb_bc_frac_high_cmip7.data
    print('Realised bb_bc')

bb_oc_cmip7 = iris.load_cube(cmip7_bb_path('OC'), constraint_1850)
bb_oc_agri_cmip7 = iris.load_cube(cmip7_bb_percent_path('OCpercentageAGRI'), constraint_1850)
bb_oc_peat_cmip7 = iris.load_cube(cmip7_bb_percent_path('OCpercentagePEAT'), constraint_1850)
bb_oc_sava_cmip7 = iris.load_cube(cmip7_bb_percent_path('OCpercentageSAVA'), constraint_1850)
bb_oc_borf_cmip7 = iris.load_cube(cmip7_bb_percent_path('OCpercentageBORF'), constraint_1850)
bb_oc_defo_cmip7 = iris.load_cube(cmip7_bb_percent_path('OCpercentageDEFO'), constraint_1850)
bb_oc_temf_cmip7 = iris.load_cube(cmip7_bb_percent_path('OCpercentageTEMF'), constraint_1850)
bb_oc_frac_low_cmip7 = 0.01 * (bb_oc_agri_cmip7 + bb_oc_peat_cmip7 + bb_oc_sava_cmip7)
bb_oc_frac_high_cmip7 = 0.01 * (bb_oc_borf_cmip7 + bb_oc_defo_cmip7 + bb_oc_temf_cmip7)
if force_load:
    _ = bb_oc_frac_low_cmip7.data
    print('Realised bb_oc low')
    _ = bb_oc_frac_high_cmip7.data
    print('Realised bb_oc high')

bb_lo_cmip7 = bb_bc_cmip7*bb_bc_frac_low_cmip7  + bb_oc_cmip7*bb_oc_frac_low_cmip7
bb_hi_cmip7 = bb_bc_cmip7*bb_bc_frac_high_cmip7 + bb_oc_cmip7*bb_oc_frac_high_cmip7

if force_load:
    _ = bb_lo_cmip7.data
    _ = bb_hi_cmip7.data
    print('LO, HI done')

# Regrid requires matching coordinate systems
set_coord_system(bb_lo_cmip7)
set_coord_system(bb_hi_cmip7)

# This data is missing over oceans, so needs to be filled with zero for the model
bb_lo_cmip7.data = bb_lo_cmip7.data.filled(0.)
bb_hi_cmip7.data = bb_hi_cmip7.data.filled(0.)

bb_lo_esm16 = bb_lo_cmip7.regrid(mask_esm15, interpolation_scheme)
bb_hi_esm16 = bb_hi_cmip7.regrid(mask_esm15, interpolation_scheme)

zero_poles(bb_lo_esm16)
zero_poles(bb_hi_esm16)

bb_lo_esm16.attributes['STASH'] = iris.fileformats.pp.STASH(model=1, section=0, item=130)
bb_hi_esm16.attributes['STASH'] = iris.fileformats.pp.STASH(model=1, section=0, item=131)

save_ancil([bb_lo_esm16, bb_hi_esm16],
           '/g/data/tm70/mrd599/esm16_aerosols/Bio_1850_cmip7.anc')
