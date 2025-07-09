from cmip7_ancil_paths import (
        ANCIL_TARGET_PATH,
        ESM_PI_AEROSOL_REL_PATH)
from cmip7_ancil_common import join_pathname


ESM_PI_AEROSOL_SAVE_DIR = join_pathname(
        ANCIL_TARGET_PATH,
        ESM_PI_AEROSOL_REL_PATH)


def zero_poles(cube):
    # Polar values should have no longitude dependence
    # For aerosol emissions they should be zero
    latdim = cube.coord_dims('latitude')
    assert latdim == (1,)
    cube.data[:, 0] = 0.0
    cube.data[:, -1] = 0.0
