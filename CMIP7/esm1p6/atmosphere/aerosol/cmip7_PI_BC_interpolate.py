# Interpolate CMIP7 PI BC emissions to ESM1-6 grid
from aerosol.cmip7_PI_aerosol_anthro import (
        cmip7_pi_aerosol_anthro_interpolate)

cmip7_pi_aerosol_anthro_interpolate(
        'BC',
        stash_item=129,
        ancil_filename='BC_1850_cmip7.anc')
