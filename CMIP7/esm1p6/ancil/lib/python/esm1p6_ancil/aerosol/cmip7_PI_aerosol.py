'''
Generics for CMIP7 pre-industrial (PI) aerosol processing.
'''
from pathlib import Path

from cmip7_ancil_constants import ANCIL_TODAY


def esm_pi_aerosol_ancil_dirpath(ancil_root_dirname):
    '''
    Return the directory path to save the ESM1.6 pre-industrial aerosol ancil files.
    '''
    return (
        Path(ancil_root_dirname)
        / "modern"
        / "pre-industrial"
        / "atmosphere"
        / "aerosol"
    )


def esm_pi_aerosol_save_dirpath(args):
    '''
    Return the directory path to save the ESM1.6 pre-industrial aerosol ancil files.
    '''
    return (
        esm_pi_aerosol_ancil_dirpath(args.ancil_target_dirname)
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )
