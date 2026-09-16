""" This contains all the common functions for generating the ESM1.5 historical forcing ancil files. """

from pathlib import Path

from cmip7_inputs.models.access_esm1p6.generators._constants import TODAY

def esm_hi_forcing_save_dirpath(ancil_target_dirname) -> Path:
    '''
    Return the directory path to save the ESM1.5 historical forcing ancil files.
    '''
    return (
        Path(ancil_target_dirname)
        / "modern"
        / "historical"
        / "atmosphere"
        / "forcing"
        / "resolution_independent"
        / TODAY
    )