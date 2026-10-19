from argparse import ArgumentParser
from pathlib import Path

from cmip7_ancil_argparse import ext_parser
from cmip7_SM import (
    CMIP7_SM_BEG_YEAR,
    CMIP7_SM_END_YEAR,
    CMIP7_SM_EXT_END_YEAR,
)
from dataset import DatasetConfig
from ghg.cmip7_ghg import GHG_MOLAR_MASS
from ghg.cmip7_ghg_series import (
    cmip7_ghg_update_namelists_file,
    load_cmip7_ghg_series_mmr,
)


def parse_args():
    """Parse command-line arguments for CMIP7 ScenarioMIP greenhouse gas
    generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing config, path,
            scenario, and extension parameters.
    """
    parser = ArgumentParser(
        parents=[ext_parser()],
        prog="cmip7_SM_ghg_generate",
        description=(
            "Generate input files from CMIP7 ScenarioMIP "
            "greenhouse gas forcings"
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
    parser.add_argument("--scenario", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    target_end_year = (
        (args.end_year or CMIP7_SM_EXT_END_YEAR)
        if args.ext
        else CMIP7_SM_END_YEAR
    )

    config = DatasetConfig.from_yaml(args.config, section=args.scenario)
    datasets = config.to_datasets_by_variable(GHG_MOLAR_MASS.keys())

    ext_datasets = None
    if args.ext:
        ext_section = f"{args.scenario}-ext"
        ext_config = DatasetConfig.from_yaml(args.config, section=ext_section)
        ext_datasets = ext_config.to_datasets_by_variable(GHG_MOLAR_MASS.keys())

    ghg_mmr_dict = dict()
    for ghg in GHG_MOLAR_MASS:
        ext_ds = ext_datasets[ghg] if ext_datasets else None
        series = load_cmip7_ghg_series_mmr(
            datasets[ghg],
            ghg,
            CMIP7_SM_BEG_YEAR,
            target_end_year,
            ext_dataset=ext_ds,
        )
        ghg_mmr_dict[ghg] = series

    # Patch the greenhouse gas namelist.
    cmip7_ghg_update_namelists_file(
        ghg_mmr_dict,
        CMIP7_SM_BEG_YEAR,
        target_end_year,
        config_dir=args.config_dir,
    )
