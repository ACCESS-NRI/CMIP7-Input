from argparse import ArgumentParser
from pathlib import Path

import f90nml
import iris
from cmip7_PI import CMIP7_PI_YEAR
from dataset import DatasetConfig
from ghg.cmip7_ghg import (
    GHG_MOLAR_MASS,
    cmip7_ghg_mmr,
    cmip7_pro_greg_date_constraint_from_years,
)


def parse_args():
    """Parse command-line arguments for CMIP7 pre-industrial greenhouse gas
    generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing config and path
            parameters.
    """
    parser = ArgumentParser(
        prog="cmip7_PI_ghg_generate",
        description=(
            "Generate input files from "
            "CMIP7 pre-industrial greenhouse gas forcings"
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


def load_cmip7_pi_ghg_mmr(dataset, ghg):
    """Load the pre-industrial annual greenhouse gas concentration and convert
    to mass mixing ratio.

    Args:
        dataset (Dataset or Path or str): Dataset instance for the greenhouse
            gas.
        ghg (str): Greenhouse gas species name (e.g. 'co2', 'ch4', 'n2o').

    Returns:
        float or numpy.ndarray: Pre-industrial mass mixing ratio (kg gas / kg
            dry air) for year 1850.
    """
    filepath = (
        str(dataset.to_path()) if hasattr(dataset, "to_path") else str(dataset)
    )

    # Read in the CMIP7 cube
    full_cube = iris.load_cube(filepath)

    # Check that we have the right greenhouse gas
    variable_id = full_cube.metadata.attributes["variable_id"]
    assert ghg == variable_id

    # Extract the pre-industrial year
    date_constraint = cmip7_pro_greg_date_constraint_from_years(
        CMIP7_PI_YEAR, CMIP7_PI_YEAR
    )
    pi_cube = full_cube.extract(date_constraint)

    # Determine the mass mixing ratio
    return cmip7_ghg_mmr(pi_cube, ghg)


def cmip7_pi_ghg_patch(ghg_mmr_dict, config_dir=None):
    """Patch the greenhouse gas variables in the RUN_Radiation namelist.

    Args:
        ghg_mmr_dict (dict): Dictionary mapping gas names ('co2', 'n2o', 'ch4',
            etc.) to scalar pre-industrial mass mixing ratios.
        config_dir (pathlib.Path or str, optional): Configuration repository
            working directory containing atmosphere/namelists. Defaults to
            Path.cwd().

    Raises:
        FileNotFoundError: If atmosphere/namelists does not exist.
    """
    GHG_PI_NAME = {
        "co2": "CO2_MMR",
        "n2o": "N2OMMR",
        "ch4": "CH4MMR",
        "cfc11": "C11MMR",
        "cfc12": "C12MMR",
        "cfc113": "C113MMR",
        "hcfc22": "HCFC22MMR",
        "hfc125": "HFC125MMR",
        "hfc134a": "HFC134AMMR",
    }

    namelist_dict = dict()
    for ghg in ghg_mmr_dict:
        namelist_dict[GHG_PI_NAME[ghg]] = ghg_mmr_dict[ghg]
    patch = {"RUN_Radiation": namelist_dict}
    patch_namelist = f90nml.namelist.Namelist(patch)
    # Set the floating point format to the right value
    patch_namelist.float_format = ".4e"
    # The floating point format is ignored unless
    # you print the namelist or convert it to a string
    patch_str = str(patch_namelist)
    parser = f90nml.Parser()
    patch_str_namelist = parser.reads(patch_str)

    # Create a new namelist by patching the original namelist
    config_dir_path = Path(config_dir) if config_dir is not None else Path.cwd()
    pi_ghg_namelist_filepath = config_dir_path / "atmosphere" / "namelists"
    if not pi_ghg_namelist_filepath.exists():
        raise FileNotFoundError(
            f"Namelist file {pi_ghg_namelist_filepath} does not exist"
        )
    new_namelist_filepath = pi_ghg_namelist_filepath.with_suffix(".nml.patched")
    parser.read(
        pi_ghg_namelist_filepath, patch_str_namelist, new_namelist_filepath
    )

    # Replace the original namelist
    new_namelist_filepath.replace(pi_ghg_namelist_filepath)


if __name__ == "__main__":
    args = parse_args()

    config = DatasetConfig.from_yaml(args.config)
    datasets = config.to_datasets_by_variable(GHG_MOLAR_MASS.keys())

    ghg_mmr_dict = dict()
    for ghg in GHG_MOLAR_MASS:
        ghg_mmr_dict[ghg] = load_cmip7_pi_ghg_mmr(datasets[ghg], ghg)

    # Patch the greenhouse gas variables in the RUN_Radiation namelist
    cmip7_pi_ghg_patch(ghg_mmr_dict, config_dir=args.config_dir)
