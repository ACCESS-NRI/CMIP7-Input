# Interpolate CMIP7 PI Biomass burning emissions to ESM1.6 grid

from aerosol.cmip7_HI_aerosol import ESM_HI_AEROSOL_SAVE_DIR
from aerosol.cmip7_HI_aerosol_biomass import (
        load_cmip7_hi_aerosol_biomass,
        load_cmip7_hi_aerosol_biomass_percentage)
from aerosol.cmip7_aerosol_biomass import save_cmip7_aerosol_biomass


save_cmip7_aerosol_biomass(
        load_cmip7_hi_aerosol_biomass_percentage,
        load_cmip7_hi_aerosol_biomass,
        ESM_HI_AEROSOL_SAVE_DIR,
        'Bio_1849_2015_cmip7.anc')
