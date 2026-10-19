"""Modular command-line argument parsers for CMIP7 ancillary generation
tasks.
"""

from argparse import ArgumentParser
from pathlib import Path


def config_parser():
    """Create an argument parser for the dataset configuration file.

    Returns:
        argparse.ArgumentParser: Parser defining the ``--config`` argument,
            the path of the ``datasetconfig.yaml`` file that identifies the
            input4MIPs datasets (default ``datasetconfig.yaml``).
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("datasetconfig.yaml"),
        help="Path to dataset configuration YAML file",
    )
    return parser


def dms_filename_parser(dms_ancil_filename=None):
    """Create an argument parser for DMS (dimethyl sulfide) background aerosol
    ancillary parameters.

    Args:
        dms_ancil_filename (str, optional): Default filename for the DMS
            ancillary file.

    Returns:
        argparse.ArgumentParser: Parser defining ``--esm15-aerosol-version``
            and ``--dms-ancil-filename`` arguments.
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--esm15-aerosol-version")
    parser.add_argument("--dms-ancil-filename", default=dms_ancil_filename)
    return parser


def pad_parser():
    """Create an argument parser for temporal padding control.

    Returns:
        argparse.ArgumentParser: Parser defining the ``--pad`` boolean flag to
            duplicate bounding years for temporal interpolation.
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--pad", action="store_true")
    return parser


def grid_parser():
    """Create an argument parser for model horizontal grid resolution and mask
    configuration.

    Returns:
        argparse.ArgumentParser: Parser defining ``--esm-grid-rel-dirname`` and
            ``--esm15-grid-version`` arguments.
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--esm-grid-rel-dirname")
    parser.add_argument("--esm15-grid-version")
    return parser


def path_parser():
    """Create an argument parser for filesystem directory paths.

    Returns:
        argparse.ArgumentParser: Parser defining ``--ancil-target-dirname``,
            ``--cmip7-source-data-dirname``, and ``--esm15-inputs-dirname``
            arguments.
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--ancil-target-dirname")
    parser.add_argument("--cmip7-source-data-dirname")
    parser.add_argument("--esm15-inputs-dirname")
    return parser


def ext_parser():
    """Create an argument parser for ScenarioMIP timeline extension (2022-2150)
    parameters.

    Returns:
        argparse.ArgumentParser: Parser defining extension toggles (``--ext``)
            and override targets (``--end-year``).
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "--ext",
        action="store_true",
        default=False,
        help=(
            "Extend forcing from CMIP7_SM_END_YEAR (2100) to "
            "CMIP7_SM_EXT_END_YEAR (2150)"
        ),
    )
    parser.add_argument(
        "--end-year", type=int, default=None, help="Override target end year"
    )
    return parser
