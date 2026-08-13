'''
CMIP7 pre-industrial (PI) emissions aerosol OCFF interpolation functions.
This module provides a function to interpolate CMIP7 pre-industrial (PI) emissions OC data to the ESM1.6 grid.

OCFF = Organic Carbon from Fossil Fuel Combustion.
'''
from aerosol.cmip7_PI_aerosol_anthro import (
    cmip7_pi_aerosol_anthro_interpolate,
    parse_args,
)

if __name__ == "__main__":
    '''
    Interpolate CMIP7 pre-industrial (PI) OCFF emissions to the ESM1.6 grid and save as an ancillary file.
    '''
    args = parse_args(species="OC")

    cmip7_pi_aerosol_anthro_interpolate(args, species="OC", stash_item=135)
