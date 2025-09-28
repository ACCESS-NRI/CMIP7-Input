from argparse import ArgumentParser
from pathlib import Path

import f90nml
import iris
from cmip7_ancil_argparse import dataset_parser, path_parser
from cmip7_PI import CMIP7_PI_YEAR
from ghg.cmip7_ghg import (
    GHG_MOLAR_MASS,
    cmip7_ghg_dirpath,
    cmip7_ghg_filename,
    cmip7_ghg_mmr,
    cmip7_pro_greg_date_constraint_from_years,
)


def parse_args():
    parser = ArgumentParser(
        parents=[path_parser(), dataset_parser()],
        prog="cmip7_PI_ghg_generate",
        description=(
            "Generate input files from "
            "CMIP7 pre-industrial greenhouse gas forcings"
        ),
    )
    parser.add_argument("--dataset-date-range")
    return parser.parse_args()


def load_cmip7_pi_ghg_mmr(args, ghg):
    cmip7_filepath = cmip7_ghg_dirpath(args, ghg) / cmip7_ghg_filename(
        args, ghg
    )

    # Read in the CMIP7 cube
    full_cube = iris.load_cube(cmip7_filepath)

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


def cmip7_pi_ghg_patch(ghg_mmr_dict):
    """
    Patch the greenhouse gas variables in the RUN_Radiation namelist
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
    # Use ghg_mmr_dict to create a ghg namelist dict
    ghg_namelist_dict = dict()
    for ghg in ghg_mmr_dict:
        ghg_namelist_dict[GHG_PI_NAME[ghg]] = ghg_mmr_dict[ghg]
    # Create a patch namelist from the ghg namelist dict
    rad_namelist_name = "RUN_Radiation"
    ghg_patch_dict = {rad_namelist_name: ghg_namelist_dict}
    ghg_patch_namelist = f90nml.namelist.Namelist(ghg_patch_dict)
    # Read the original namelist from the namelist file 
    parser = f90nml.Parser()
    pi_ghg_namelist_filepath = Path("atmosphere") / "namelists"
    if not pi_ghg_namelist_filepath.exists():
        raise FileNotFoundError(
            f"Namelist file {pi_ghg_namelist_filepath} does not exist"
        )
    all_namelists = parser.read(pi_ghg_namelist_filepath)
    rad_namelist_dict = all_namelists[rad_namelist_name]
    # Create a patch namelist from the rad namelist dict
    rad_patch_dict = {rad_namelist_name: rad_namelist_dict}
    rad_patch_namelist = f90nml.namelist.Namelist(rad_patch_dict)  
    # Set the floating point format to the right value for the rad namelist
    rad_patch_namelist.float_format = ".5g"
    rad_patch_namelist.uppercase = True
    # Use the ghg patch namelist to patch the rad patch namelist
    rad_patch_namelist.patch(ghg_patch_namelist)
    # Create a new namelist file by patching the original namelist file
    new_namelist_filepath = pi_ghg_namelist_filepath.with_suffix(".nml.patched")
    parser.read(
        pi_ghg_namelist_filepath, rad_patch_namelist, new_namelist_filepath
    )

    # Replace the original namelist file
    new_namelist_filepath.replace(pi_ghg_namelist_filepath)


if __name__ == "__main__":
    args = parse_args()

    ghg_mmr_dict = dict()
    for ghg in GHG_MOLAR_MASS:
        ghg_mmr_dict[ghg] = load_cmip7_pi_ghg_mmr(args, ghg)

    # Patch the greenhouse gas variables in the RUN_Radiation namelist
    cmip7_pi_ghg_patch(ghg_mmr_dict)
