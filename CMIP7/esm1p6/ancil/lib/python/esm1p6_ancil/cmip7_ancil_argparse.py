"""Modular command-line argument parsers for CMIP7 ancillary generation
tasks.
"""

from argparse import ArgumentParser


def dataset_parser():
    """Create an argument parser for CMIP7 input4MIPs dataset identification.

    Returns:
        argparse.ArgumentParser: Parser defining ``--dataset-version`` and
            ``--dataset-vdate`` arguments.
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--dataset-version")
    parser.add_argument("--dataset-vdate")
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


def percent_parser():
    """Create an argument parser for percentage-based emission distribution
    datasets.

    Returns:
        argparse.ArgumentParser: Parser defining ``--percent-version``,
            ``--percent-vdate``, and ``--percent-date-range`` arguments.
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--percent-version")
    parser.add_argument("--percent-vdate")
    parser.add_argument("--percent-date-range")
    return parser


def common_parser():
    """Create a composite argument parser combining path, grid, and dataset
    options.

    Returns:
        argparse.ArgumentParser: Composite parent parser combining
       :func:`path_parser`, :func:`grid_parser`, and :func:`dataset_parser`.
    """
    parser = ArgumentParser(
        parents=[path_parser(), grid_parser(), dataset_parser()], add_help=False
    )
    return parser


def ext_parser():
    """Create an argument parser for ScenarioMIP timeline extension (2022-2150)
    parameters.

    Returns:
        argparse.ArgumentParser: Parser defining extension toggles (``--ext``),
            override targets (``--end-year``), and extension dataset
            coordinates for surface and aircraft emissions.
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
    parser.add_argument(
        "--dataset-ext-version", help="Version of extension dataset"
    )
    parser.add_argument(
        "--dataset-ext-vdate", help="Version date of extension dataset"
    )
    parser.add_argument(
        "--dataset-ext-date-range", help="Date range of extension dataset"
    )
    parser.add_argument(
        "--dataset-air-ext-version",
        help="Version of aircraft extension dataset",
    )
    parser.add_argument(
        "--dataset-air-ext-vdate",
        help="Version date of aircraft extension dataset",
    )
    parser.add_argument(
        "--dataset-air-ext-date-range",
        help="Date range of aircraft extension dataset",
    )
    return parser
