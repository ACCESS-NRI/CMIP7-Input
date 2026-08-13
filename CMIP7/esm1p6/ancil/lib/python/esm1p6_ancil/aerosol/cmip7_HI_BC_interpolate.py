'''
CMIP7 historical emissions BC data interpolation function.
This module provides a function to interpolate CMIP7 historical emissions BC data to the ESM1.6 grid.

BC = Black Carbon.
'''
from aerosol.cmip7_HI_aerosol_anthro import (
    cmip7_hi_aerosol_anthro_interpolate,
    parse_args,
)

if __name__ == "__main__":
    '''
    Interpolate CMIP7 historical emissions BC data to the ESM1.6 grid.
    '''
    args = parse_args(species="BC")

    cmip7_hi_aerosol_anthro_interpolate(args, species="BC", stash_item=129)
