# Interpolate CMIP7 HI OCFF emissions to ESM1.6 grid
from .aerosol.cmip7_HI_aerosol_anthro import (
    cmip7_hi_aerosol_anthro_interpolate,
    parse_args,
)

if __name__ == "__main__":
    args = parse_args(species="OC")

    cmip7_hi_aerosol_anthro_interpolate(args, species="OC", stash_item=135)
