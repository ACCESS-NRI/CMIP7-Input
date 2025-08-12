from cmip7_ancil_common import join_pathname
from cmip7_ancil_paths import ANCIL_TARGET_PATH

import os


ESM15_PI_AEROSOL_VERSION = os.environ['ESM15_PI_AEROSOL_VERSION']
ESM_PI_AEROSOL_REL_PATH = 'modern/pre-industrial/atmosphere/aerosol'
ESM_PI_AEROSOL_SAVE_DIR = join_pathname(
        ANCIL_TARGET_PATH,
        ESM_PI_AEROSOL_REL_PATH)
