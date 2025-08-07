# Interpolate CMIP7 HI OCFF emissions to ESM1.6 grid
from aerosol.cmip7_HI_aerosol_anthro import (
        parse_args,
        cmip7_hi_aerosol_anthro_interpolate)


SAVE_FILENAME = 'OCFF_1849_2015_cmip7.anc'


if __name__ == '__main__':

    args = parse_args(species='OC', save_filename=SAVE_FILENAME)

    cmip7_hi_aerosol_anthro_interpolate(args, species='OC', stash_item=135)
