"""ScenarioMIP projection experiment (SM) configuration constants and save path
resolution.
"""

from pathlib import Path

from cmip7_ancil_constants import ANCIL_TODAY

CMIP7_SM_BEG_YEAR = 2022
CMIP7_SM_END_YEAR = 2100
CMIP7_SM_EXT_END_YEAR = 2150


def esm_sm_forcing_save_dirpath(args):
    """Construct destination directory path for resolution-independent
    ScenarioMIP forcing ancillaries.

    Args:
        args (argparse.Namespace): Parsed CLI arguments containing
            ``ancil_target_dirname``.

    Returns:
        pathlib.Path: Target directory path in ``scen7-common/`` stamped with
            current generation date token.
    """
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "scen7-common"
        / "atmosphere"
        / "forcing"
        / "resolution_independent"
        / ANCIL_TODAY
    )
