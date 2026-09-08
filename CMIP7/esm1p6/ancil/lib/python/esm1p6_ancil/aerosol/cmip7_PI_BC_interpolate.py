# Interpolate CMIP7 PI BC emissions to ESM1-6 grid
from aerosol.cmip7_PI_aerosol_anthro import (
    cmip7_pi_aerosol_anthro_interpolate,
    parse_args,
)

if __name__ == "__main__":
    '''
    Interpolate CMIP7 pre-industrial (PI) BC emissions to the ESM1.6 grid and save as an ancillary file.'''
    args = parse_args(species="BC")

    cmip7_pi_aerosol_anthro_interpolate(args, species="BC", stash_item=129)
