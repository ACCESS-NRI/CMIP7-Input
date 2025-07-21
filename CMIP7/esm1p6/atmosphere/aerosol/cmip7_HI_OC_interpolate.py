# Interpolate CMIP7 HI OCFF emissions to ESM1.6 grid
from aerosol.cmip7_HI_aerosol_anthro import (
        cmip7_hi_aerosol_anthro_interpolate)

cmip7_hi_aerosol_anthro_interpolate(
        'OC',
        stash_item=135,
        ancil_filename='OCFF_1849_2015_cmip7.anc')
