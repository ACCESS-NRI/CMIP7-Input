# Interpolate CMIP7 PI Biomass burning emissions to ESM1.6 grid

from aerosol.cmip7_PI_aerosol import ESM_PI_AEROSOL_SAVE_DIR
from aerosol.cmip7_PI_aerosol_biomass import (
        load_cmip7_pi_aerosol_biomass,
        load_cmip7_pi_aerosol_biomass_percentage)
from aerosol.cmip7_aerosol_biomass import save_cmip7_aerosol_biomass


save_cmip7_aerosol_biomass(
        load_cmip7_pi_aerosol_biomass_percentage,
        load_cmip7_pi_aerosol_biomass,
        ESM_PI_AEROSOL_SAVE_DIR,
        'Bio_1850_cmip7.anc')
