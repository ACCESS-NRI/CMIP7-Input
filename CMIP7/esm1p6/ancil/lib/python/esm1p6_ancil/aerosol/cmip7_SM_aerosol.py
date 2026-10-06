from pathlib import Path

from cmip7_ancil_constants import ANCIL_TODAY


def esm_sm_aerosol_ancil_dirpath(args):
    """Construct the base directory path for ScenarioMIP aerosol ancillaries.

    Args:
        args (argparse.Namespace): Command-line arguments containing
            ancil_target_dirname and scenario.

    Returns:
        pathlib.Path: Directory path under
            modern/scen7-{scenario}/atmosphere/aerosol.
    """
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / f"scen7-{args.scenario}"
        / "atmosphere"
        / "aerosol"
    )


def esm_sm_aerosol_save_dirpath(args):
    """Construct the target directory path for saving ScenarioMIP aerosol
    ancillary files.

    Args:
        args (argparse.Namespace): Command-line arguments containing output
            path configuration (ancil_target_dirname, scenario,
            esm_grid_rel_dirname).

    Returns:
        pathlib.Path: Target directory path with resolution and date stamps.
    """
    return (
        esm_sm_aerosol_ancil_dirpath(args)
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )
