'''
    Interpolate CMIP7 ScenarioMIP emissions OCFF emissions to ESM1.6 grid.
    This module provides a function to interpolate CMIP7 ScenarioMIP emissions OCFF emissions data to the ESM1.6 grid.
    OCFF = Organic Carbon from Fossil Fuel Combustion.
'''
from aerosol.cmip7_SM_aerosol_anthro import (
    cmip7_sm_aerosol_anthro_interpolate,
    parse_args,
)

# TODO: This module identical to cmip7_HI_OC_interpolate.py except for the function names. 
# Consider merging them into a single module with experiment argument.
if __name__ == "__main__":
    '''
    Interpolate CMIP7 ScenarioMIP OCFF emissions to ESM1.6 grid.  
    '''
    args = parse_args(species="OC")

    cmip7_sm_aerosol_anthro_interpolate(args, species="OC", stash_item=135)
