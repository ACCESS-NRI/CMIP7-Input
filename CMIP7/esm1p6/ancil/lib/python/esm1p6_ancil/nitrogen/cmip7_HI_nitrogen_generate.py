from argparse import ArgumentParser
from pathlib import Path

from cmip7_ancil_argparse import grid_parser, path_parser
from cmip7_ancil_common import extend_years
from cmip7_ancil_constants import ANCIL_TODAY
from dataset import DatasetConfig
from nitrogen.cmip7_nitrogen import (
    NITROGEN_SPECIES,
    load_cmip7_nitrogen,
    regrid_cmip7_nitrogen,
    save_cmip7_nitrogen,
)


def parse_args():
    """Parse command-line arguments for historical nitrogen ancillary
    generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, grid,
            config, and save filename parameters.
    """
    parser = ArgumentParser(
        parents=[path_parser(), grid_parser()],
        prog="cmip7_HI_nitrogen_generate",
        description=(
            "Generate input files from CMIP7 historical nitrogen forcings"
        ),
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("datasetconfig.yaml"),
        help="Path to dataset configuration YAML file",
    )
    parser.add_argument("--save-filename")
    return parser.parse_args()


def esm_hi_nitrogen_save_dirpath(args):
    """Construct the destination directory path for historical nitrogen
    ancillary files.

    Args:
        args (argparse.Namespace): Command-line arguments containing output
            path configuration.

    Returns:
        pathlib.Path: Target directory path under
            modern/historical/atmosphere/land/biogeochemistry/.
    """
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "historical"
        / "atmosphere"
        / "land"
        / "biogeochemistry"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


if __name__ == "__main__":
    args = parse_args()

    # Load the CMIP7 datasets
    config = DatasetConfig.from_yaml(args.config)
    datasets = config.to_datasets_by_variable(NITROGEN_SPECIES)
    nitrogen_cube = load_cmip7_nitrogen(datasets)

    # Regrid to match the ESM1.5 mask and extend the time series
    esm_cube = extend_years(regrid_cmip7_nitrogen(args, nitrogen_cube))
    # Save the ancillary
    save_cmip7_nitrogen(args, esm_cube, esm_hi_nitrogen_save_dirpath)
