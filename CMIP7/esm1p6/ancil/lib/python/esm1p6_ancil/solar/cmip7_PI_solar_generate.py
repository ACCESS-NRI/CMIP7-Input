from argparse import ArgumentParser
from pathlib import Path

import f90nml
from cmip7_ancil_argparse import config_parser
from dataset import DatasetConfig
from solar.cmip7_solar import load_cmip7_solar_cube


def parse_args():
    """Parse command-line arguments for pre-industrial solar forcing
    generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing the dataset
            configuration file and the configuration repository directory.
    """
    parser = ArgumentParser(
        parents=[config_parser()],
        prog="cmip7_PI_solar_generate",
        description=(
            "Generate input files from CMIP7 pre-industrial solar forcings"
        ),
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path.cwd(),
        help="Path to configuration repository containing atmosphere/",
    )
    return parser.parse_args()


def cmip7_pi_solar_patch(solar_irradiance, config_dir):
    """Patch the SC variable in the coupling namelist.

    Args:
        solar_irradiance (float): Pre-industrial solar constant irradiance
            value (W/m2).
        config_dir (pathlib.Path): Configuration repository directory.
    """
    patch = {"coupling": {"SC": solar_irradiance}}
    patch_namelist = f90nml.namelist.Namelist(patch)
    # Set the floating point format to the right value
    patch_namelist.float_format = ".3f"
    # The floating point format is ignored unless
    # you print the namelist or convert it to a string
    patch_str = str(patch_namelist)
    parser = f90nml.Parser()
    patch_str_namelist = parser.reads(patch_str)

    # Create a new namelist by patching the original namelist
    pi_solar_namelist_filepath = config_dir / "atmosphere" / "input_atm.nml"

    new_namelist_filepath = pi_solar_namelist_filepath.with_suffix(
        ".nml.patched"
    )
    parser.read(
        pi_solar_namelist_filepath, patch_str_namelist, new_namelist_filepath
    )

    # Replace the original namelist
    new_namelist_filepath.replace(pi_solar_namelist_filepath)


if __name__ == "__main__":
    args = parse_args()

    config = DatasetConfig.from_yaml(args.config)
    solar_irradiance_cube = load_cmip7_solar_cube(config.to_dataset())
    solar_irradiance = solar_irradiance_cube[0].data

    # Patch the SC variable in the coupling namelist
    cmip7_pi_solar_patch(solar_irradiance, args.config_dir)
