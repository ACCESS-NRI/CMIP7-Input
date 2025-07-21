# Interpolate CMIP7 HI BC emissions to ESM1.6 grid
from aerosol.cmip7_HI_aerosol_anthro import (
        cmip7_hi_aerosol_anthro_interpolate)

cmip7_hi_aerosol_anthro_interpolate(
        'BC',
        stash_item=129,
        ancil_filename='BC_1849_2015_cmip7.anc')
