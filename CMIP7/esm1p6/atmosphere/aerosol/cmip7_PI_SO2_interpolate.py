# Interpolate CMIP7 PI SO2 emissions to ESM1.6 grid

from aerosol.cmip7_PI_aerosol import (
        ESM15_PI_AEROSOL_VERSION,
        ESM_PI_AEROSOL_REL_PATH,
        ESM_PI_AEROSOL_SAVE_DIR)
from aerosol.cmip7_PI_aerosol_anthro import (
        CMIP7_PI_AEROSOL_ANTHRO_DATE_RANGE,
        load_cmip7_pi_aerosol_anthro)
from aerosol.cmip7_SO2_interpolate import (
        load_dms,
        save_cmip7_so2_aerosol_anthro)

from cmip7_ancil_paths import (
        ESM15_INPUTS_PATH,
        ESM_GRID_DIRNAME)
from cmip7_PI import fix_esm15_pi_ancil_date


def load_pi_dms():
    # Use the CMIP6 DMS
    ESM15_PI_DMS_ANCIL_DIRNAME = str(
            ESM15_INPUTS_PATH
            / ESM_PI_AEROSOL_REL_PATH
            / ESM_GRID_DIRNAME
            / ESM15_PI_AEROSOL_VERSION)
    ESM15_PI_DMS_ANCIL_FILENAME = 'scycl_1850_ESM1_v4.anc'
    return load_dms(
            ESM15_PI_DMS_ANCIL_DIRNAME,
            ESM15_PI_DMS_ANCIL_FILENAME,
            fix_esm15_pi_ancil_date)


save_cmip7_so2_aerosol_anthro(
        load_cmip7_pi_aerosol_anthro,
        CMIP7_PI_AEROSOL_ANTHRO_DATE_RANGE,
        load_pi_dms,
        ESM_PI_AEROSOL_SAVE_DIR,
        'scycl_1850_cmip7.anc')
