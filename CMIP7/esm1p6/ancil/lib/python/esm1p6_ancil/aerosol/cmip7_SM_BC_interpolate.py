# Interpolate CMIP7 HI BC emissions to ESM1.6 grid
'''
    Interpolate CMIP7 ScenarioMIP BC emissions to ESM1.6 grid.
    This module provides a function to interpolate CMIP7 ScenarioMIP BC emissions data to the ESM1.6 grid.
    BC = Black Carbon.
'''
from aerosol.cmip7_SM_aerosol_anthro import (
    cmip7_sm_aerosol_anthro_interpolate,
    parse_args,
)

if __name__ == "__main__":
    '''
    Interpolate CMIP7 ScenarioMIP BC emissions to ESM1.6 grid.
    '''
    args = parse_args(species="BC")

    cmip7_sm_aerosol_anthro_interpolate(args, species="BC", stash_item=129)
