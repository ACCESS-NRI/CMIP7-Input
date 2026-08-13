'''
    Generic functions for the CMIP7 ScenarioMIP aerosol ancil file processing scripts.
'''

from pathlib import Path

from cmip7_ancil_constants import ANCIL_TODAY

# TODO: I think this functions is only used once by the function esm_sm_aerosol_save_dirpath, 
# so it could be removed and the code in that function could be used directly instead.
def esm_sm_aerosol_ancil_dirpath(args):
    '''
    Return the directory path to the ESM1.6 ScenarioMIP aerosol ancil file.
    '''
    return (
        Path(args.ancil_target_dirname)
        / "scenarios"
        / args.scenario
        / "atmosphere"
        / "aerosol"
    )


def esm_sm_aerosol_save_dirpath(args):
    '''
    Return the directory path to save the ESM1.6 ScenarioMIP aerosol ancil file.
    '''
    return (
        esm_sm_aerosol_ancil_dirpath(args)
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )
