# Interpolate CMIP7 PI Biomass burning emissions to ESM1-6 grid
from aerosol.cmip7_aerosol_biomass import *

# If the data are explicitly loaded
# real    1m47.602s
# user    1m30.652s
# sys     0m15.503s
# Otherwise > 20 minutes

force_load = True

def cmip7_bb_path(species):
    return cmip7_aerosol_biomass_path(
            species, 
            CMIP7_AEROSOL_BIOMASS_VERSION, 
            CMIP7_AEROSOL_BIOMASS_VDATE, 
            CMIP7_AEROSOL_BIOMASS_DATE_RANGE)

def cmip7_bb_percent_path(species):
    return cmip7_aerosol_biomass_path(
            species, 
            CMIP7_AEROSOL_BIOMASS_VERSION, 
            CMIP7_AEROSOL_BIOMASS_VDATE, 
            CMIP7_AEROSOL_BIOMASS_PERCENTAGE_DATE_RANGE)

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

save_ancil([bb_lo_esm16, bb_hi_esm16], cmip7_aerosol_save_path('Bio_1850_cmip7.anc'))
