# Interpolate CMIP7 HI SO2 emissions to ESM1.6 grid

from aerosol.cmip7_HI_aerosol import (
        ESM15_HI_AEROSOL_VERSION,
        ESM_HI_AEROSOL_REL_PATH,
        ESM_HI_AEROSOL_SAVE_DIR)
from aerosol.cmip7_HI_aerosol_anthro import (
        CMIP7_HI_AEROSOL_ANTHRO_DATE_RANGE_LIST,
        load_cmip7_hi_aerosol_anthro)
from aerosol.cmip7_SO2_interpolate import (
        load_dms,
        save_cmip7_so2_aerosol_anthro)

from cmip7_ancil_paths import (
        ESM15_INPUTS_PATH,
        ESM_GRID_DIRNAME)
from cmip7_HI import fix_esm15_hi_ancil_date


def load_hi_dms():
    # Use the CMIP6 DMS
    ESM15_HI_DMS_ANCIL_DIRNAME = str(
            ESM15_INPUTS_PATH
            / ESM_HI_AEROSOL_REL_PATH
            / ESM_GRID_DIRNAME
            / ESM15_HI_AEROSOL_VERSION)
    ESM15_HI_DMS_ANCIL_FILENAME = 'scycl_1849_2015_ESM1_v4.anc'
    return load_dms(
            ESM15_HI_DMS_ANCIL_DIRNAME,
            ESM15_HI_DMS_ANCIL_FILENAME,
            fix_esm15_hi_ancil_date)


save_cmip7_so2_aerosol_anthro(
        load_cmip7_hi_aerosol_anthro,
        CMIP7_HI_AEROSOL_ANTHRO_DATE_RANGE_LIST,
        load_hi_dms,
        ESM_HI_AEROSOL_SAVE_DIR,
        'scycl_1849_2015_cmip7.anc')
