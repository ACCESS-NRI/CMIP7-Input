'''
    This contains all the common functions for generating the ESM1.5 historical forcing ancil files.
    Originally it is the CMIP7_HI.py
'''
from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.models.access_esm1p6.generators._constants import ANCIL_TODAY
from pathlib import Path

from cmip7_inputs.models.access_esm1p6.generators._common_PI import CMIP7_PI_YEAR


CMIP7_HI_BEG_YEAR = CMIP7_PI_YEAR
# Model time interpolation requires an extra year
CMIP7_HI_END_YEAR = 2023
CMIP7_HI_NBR_YEARS = CMIP7_HI_END_YEAR + 1 - CMIP7_HI_BEG_YEAR

def esm_hi_forcing_save_dirpath(request: GenerationRequest) -> Path:
    '''
    Return the directory path to save the ESM1.5 historical forcing ancil files.
    '''
    return (
        Path(request.options['ancil_target_dirname'])
        / "modern"
        / "historical"
        / "atmosphere"
        / "forcing"
        / "resolution_independent"
        / ANCIL_TODAY
    )