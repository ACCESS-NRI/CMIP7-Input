from pathlib import Path

from cmip7_ancil_constants import ANCIL_TODAY


def esm_sm_aerosol_ancil_dirpath(args):
    return (
        Path(args.ancil_target_dirname)
        / "scenarios"
        / args.scenario
        / "atmosphere"
        / "aerosol"
    )


def esm_sm_aerosol_save_dirpath(args):
    return (
        esm_sm_aerosol_ancil_dirpath(args)
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )
