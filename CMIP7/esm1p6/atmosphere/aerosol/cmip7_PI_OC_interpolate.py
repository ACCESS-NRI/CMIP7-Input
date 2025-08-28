# Interpolate CMIP7 PI OCFF emissions to ESM1-6 grid
from aerosol.cmip7_PI_aerosol_anthro import (
    cmip7_pi_aerosol_anthro_interpolate,
    parse_args,
)

if __name__ == '__main__':
    args = parse_args(species='OC')

    cmip7_pi_aerosol_anthro_interpolate(args, species='OC', stash_item=135)
