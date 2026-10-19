from argparse import ArgumentParser
from pathlib import Path

from cmip7_HI import (
    CMIP7_HI_BEG_YEAR,
    CMIP7_HI_END_YEAR,
)
from dataset import DatasetConfig
from ghg.cmip7_ghg import GHG_MOLAR_MASS
from ghg.cmip7_ghg_series import (
    cmip7_ghg_update_namelists_file,
    load_cmip7_ghg_series_mmr,
)


def parse_args():
    """Parse command-line arguments for CMIP7 historical greenhouse gas
    generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing config and path
            parameters.
    """
    parser = ArgumentParser(
        prog="cmip7_HI_ghg_generate",
        description=(
            "Generate input files from CMIP7 historical greenhouse gas forcings"
        ),
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("datasetconfig.yaml"),
        help="Path to dataset configuration YAML file",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path.cwd(),
        help="Path to configuration repository containing atmosphere/namelists",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    config = DatasetConfig.from_yaml(args.config)
    datasets = config.to_datasets_by_variable(GHG_MOLAR_MASS.keys())

    ghg_mmr_dict = dict()
    for ghg in GHG_MOLAR_MASS:
        ghg_mmr_dict[ghg] = load_cmip7_ghg_series_mmr(
            datasets[ghg], ghg, CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR
        )

    # Patch the greenhouse gas namelist.
    cmip7_ghg_update_namelists_file(
        ghg_mmr_dict,
        CMIP7_HI_BEG_YEAR,
        CMIP7_HI_END_YEAR,
        config_dir=args.config_dir,
    )
