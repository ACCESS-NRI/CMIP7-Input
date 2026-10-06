from pathlib import Path

from cmip7_ancil_constants import ANCIL_TODAY


def esm_pi_aerosol_ancil_dirpath(ancil_root_dirname):
    """Construct the base directory path for pre-industrial aerosol
    ancillaries.

    Args:
        ancil_root_dirname (str or pathlib.Path): Root ancillary output
            directory.

    Returns:
        pathlib.Path: Directory path under modern/pre-
            industrial/atmosphere/aerosol.
    """
    return (
        Path(ancil_root_dirname)
        / "modern"
        / "pre-industrial"
        / "atmosphere"
        / "aerosol"
    )


def esm_pi_aerosol_save_dirpath(args):
    """Construct the target directory path for saving pre-industrial aerosol
    ancillary files.

    Args:
        args (argparse.Namespace): Command-line arguments containing
            ancil_target_dirname and esm_grid_rel_dirname.

    Returns:
        pathlib.Path: Target directory path with resolution and date stamps.
    """
    return (
        esm_pi_aerosol_ancil_dirpath(args.ancil_target_dirname)
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )
