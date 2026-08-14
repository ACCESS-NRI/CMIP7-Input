from pathlib import Path

from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.models.access_esm1p6.generators._constants import ANCIL_TODAY

CMIP7_SM_BEG_YEAR = 2022
CMIP7_SM_END_YEAR = 2100


def esm_sm_forcing_save_dirpath(request: GenerationRequest) -> Path:
    '''
    Return the directory path to save the ESM1.5 scenario forcing ancil files.
    '''
    return (
        Path(request.options['ancil_target_dirname'])
        / "scenarios"
        / request.options['scenario']
        / "atmosphere"
        / "forcing"
        / "resolution_independent"
        / ANCIL_TODAY
    )