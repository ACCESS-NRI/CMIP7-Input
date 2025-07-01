from pathlib import Path
import os

ANCIL_TARGET_PATH = Path(os.environ['ANCIL_TARGET_PATH'])
CMIP7_SOURCE_DATA = Path(os.environ['CMIP7_SOURCE_DATA'])
ESM15_INPUTS_PATH = Path(os.environ['ESM15_INPUTS_PATH'])

ESM_GRIDS_REL_PATH = 'modern/share/atmosphere/grids'
ESM_GRID_DIRNAME = os.environ['ESM_GRID_DIRNAME']
ESM15_GRID_VERSION = os.environ['ESM15_GRID_VERSION']
ESM16_GRID_MASK_FILE = str(
        ESM15_INPUTS_PATH / 
        ESM_GRIDS_REL_PATH / 
        ESM_GRID_DIRNAME / 
        ESM15_GRID_VERSION / 
        'qrparm.mask')

ESM_PI_AEROSOL_REL_PATH = 'modern/pre-industrial/atmosphere/aerosol'
ESM15_PI_AEROSOL_VERSION = os.environ['ESM15_PI_AEROSOL_VERSION']
