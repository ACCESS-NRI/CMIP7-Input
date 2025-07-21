# Interpolate CMIP7 PI OCFF emissions to ESM1-6 grid
from aerosol.cmip7_aerosol_anthro import cmip7_aerosol_anthro_interpolate

cmip7_aerosol_anthro_interpolate(
        'OC',
        stash_item=135,
        ancil_filename='OCFF_1850_cmip7.anc')
