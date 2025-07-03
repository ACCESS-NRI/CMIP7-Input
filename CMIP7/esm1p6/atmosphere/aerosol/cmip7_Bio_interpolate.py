# Interpolate CMIP7 PI Biomass burning emissions to ESM1-6 grid
from aerosol.cmip7_aerosol_biomass import (
        cmip7_aerosol_biomass_path,
        CMIP7_AEROSOL_BIOMASS_DATE_RANGE,
        CMIP7_AEROSOL_BIOMASS_PERCENTAGE_DATE_RANGE,
        CMIP7_AEROSOL_BIOMASS_VDATE,
        CMIP7_AEROSOL_BIOMASS_VERSION)

from aerosol.cmip7_aerosol_common import (
        cmip7_aerosol_save_path,
        CMIP7_PI_DATE_CONSTRAINT,
        interpolation_scheme,
        mask_esm15,
        save_ancil,
        set_coord_system,
        zero_poles)

import iris

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


def cmip7_bb_load_pi_percent_cube(species):
    return iris.load_cube(
            cmip7_bb_percent_path(species),
            CMIP7_PI_DATE_CONSTRAINT)


bb_bc_cmip7 = iris.load_cube(cmip7_bb_path('BC'), CMIP7_PI_DATE_CONSTRAINT)
bb_bc_agri_cmip7 = cmip7_bb_load_pi_percent_cube('BCpercentageAGRI')
bb_bc_peat_cmip7 = cmip7_bb_load_pi_percent_cube('BCpercentagePEAT')
bb_bc_sava_cmip7 = cmip7_bb_load_pi_percent_cube('BCpercentageSAVA')
bb_bc_borf_cmip7 = cmip7_bb_load_pi_percent_cube('BCpercentageBORF')
bb_bc_defo_cmip7 = cmip7_bb_load_pi_percent_cube('BCpercentageDEFO')
bb_bc_temf_cmip7 = cmip7_bb_load_pi_percent_cube('BCpercentageTEMF')
# For the low/high split follow Met Office CMIP6
# low: AGRI, PEAT, SAVA
# high: BORF, DEFO, TEMF
bb_bc_frac_low_cmip7 = (
    0.01 * (bb_bc_agri_cmip7 + bb_bc_peat_cmip7 + bb_bc_sava_cmip7))
bb_bc_frac_high_cmip7 = (
    0.01 * (bb_bc_borf_cmip7 + bb_bc_defo_cmip7 + bb_bc_temf_cmip7))
if force_load:
    _ = bb_bc_frac_low_cmip7.data
    print('Realised bb_bc low')
    _ = bb_bc_frac_high_cmip7.data
    print('Realised bb_bc high')

bb_oc_cmip7 = iris.load_cube(cmip7_bb_path('OC'), CMIP7_PI_DATE_CONSTRAINT)
bb_oc_agri_cmip7 = cmip7_bb_load_pi_percent_cube('OCpercentageAGRI')
bb_oc_peat_cmip7 = cmip7_bb_load_pi_percent_cube('OCpercentagePEAT')
bb_oc_sava_cmip7 = cmip7_bb_load_pi_percent_cube('OCpercentageSAVA')
bb_oc_borf_cmip7 = cmip7_bb_load_pi_percent_cube('OCpercentageBORF')
bb_oc_defo_cmip7 = cmip7_bb_load_pi_percent_cube('OCpercentageDEFO')
bb_oc_temf_cmip7 = cmip7_bb_load_pi_percent_cube('OCpercentageTEMF')
bb_oc_frac_low_cmip7 = (
    0.01 * (bb_oc_agri_cmip7 + bb_oc_peat_cmip7 + bb_oc_sava_cmip7))
bb_oc_frac_high_cmip7 = (
    0.01 * (bb_oc_borf_cmip7 + bb_oc_defo_cmip7 + bb_oc_temf_cmip7))
if force_load:
    _ = bb_oc_frac_low_cmip7.data
    print('Realised bb_oc low')
    _ = bb_oc_frac_high_cmip7.data
    print('Realised bb_oc high')

bb_lo_cmip7 = (
    bb_bc_cmip7*bb_bc_frac_low_cmip7 + bb_oc_cmip7*bb_oc_frac_low_cmip7)
bb_hi_cmip7 = (
    bb_bc_cmip7*bb_bc_frac_high_cmip7 + bb_oc_cmip7*bb_oc_frac_high_cmip7)

if force_load:
    _ = bb_lo_cmip7.data
    _ = bb_hi_cmip7.data
    print('LO, HI done')

# Regrid requires matching coordinate systems
set_coord_system(bb_lo_cmip7)
set_coord_system(bb_hi_cmip7)

# This data is missing over oceans,
# so needs to be filled with zero for the model
bb_lo_cmip7.data = bb_lo_cmip7.data.filled(0.)
bb_hi_cmip7.data = bb_hi_cmip7.data.filled(0.)

bb_lo_esm16 = bb_lo_cmip7.regrid(mask_esm15, interpolation_scheme)
bb_hi_esm16 = bb_hi_cmip7.regrid(mask_esm15, interpolation_scheme)

zero_poles(bb_lo_esm16)
zero_poles(bb_hi_esm16)

bb_lo_esm16.attributes['STASH'] = iris.fileformats.pp.STASH(
        model=1,
        section=0,
        item=130)
bb_hi_esm16.attributes['STASH'] = iris.fileformats.pp.STASH(
        model=1,
        section=0,
        item=131)

save_ancil(
        [bb_lo_esm16, bb_hi_esm16],
        cmip7_aerosol_save_path('Bio_1850_cmip7.anc'))
