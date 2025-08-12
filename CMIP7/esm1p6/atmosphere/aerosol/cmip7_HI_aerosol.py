from cmip7_ancil_common import join_pathname
from cmip7_ancil_paths import ANCIL_TARGET_PATH

import os


ESM15_HI_AEROSOL_VERSION = os.environ['ESM15_HI_AEROSOL_VERSION']
ESM_HI_AEROSOL_REL_PATH = 'modern/historical/atmosphere/aerosol'
ESM_HI_AEROSOL_SAVE_DIR = join_pathname(
        ANCIL_TARGET_PATH,
        ESM_HI_AEROSOL_REL_PATH)
