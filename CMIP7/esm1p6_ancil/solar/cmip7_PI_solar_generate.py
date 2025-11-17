from argparse import ArgumentParser
from pathlib import Path

import f90nml
from cmip7_ancil_argparse import common_parser
from solar.cmip7_solar import cmip7_solar_dirpath, load_cmip7_solar_cube


def parse_args():
    parser = ArgumentParser(
        parents=[common_parser()],
        prog="cmip7_PI_solar_generate",
        description=(
            "Generate input files from CMIP7 pre-industrial solar forcings"
        ),
    )
    return parser.parse_args()


def cmip7_pi_solar_patch(solar_irradiance):
    """
    Patch the SC variable in the coupling namelist
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
    pi_solar_namelist_filepath = Path("atmosphere") / "input_atm.nml"

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

    cmip7_filename = (
        f"multiple_input4MIPs_solar_CMIP_{args.dataset_version}_gn.nc"
    )
    cmip7_filepath = cmip7_solar_dirpath(args, "fx") / cmip7_filename

    solar_irradiance_cube = load_cmip7_solar_cube(cmip7_filepath)
    solar_irradiance = solar_irradiance_cube[0].data

    # Patch the SC variable in the coupling namelist
    cmip7_pi_solar_patch(solar_irradiance)
