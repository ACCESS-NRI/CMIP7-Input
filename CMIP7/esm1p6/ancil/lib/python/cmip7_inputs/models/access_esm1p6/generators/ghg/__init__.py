"""
ACCESS-ESM1.6 ghg forcing generators.

Importing this package registers all of ACCESS-ESM1.6's greenhouse gas
generators.

In here I compiled the cmip7_HI_ghg_generate.py, cmip7_PI_ghg_generate.py and cmip7_SM_ghg_generate.py into one file.
"""
from __future__ import annotations

import f90nml
import numpy as np
import iris

from pathlib import Path

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.core.registry import registry
from cmip7_inputs.models.access_esm1p6 import MODEL_ID

from cmip7_inputs.models.access_esm1p6.generators._common import cmip7_parse_args
from cmip7_inputs.models.access_esm1p6.generators._common_HI import CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR
from cmip7_inputs.models.access_esm1p6.generators._common_PI import CMIP7_PI_YEAR

from cmip7_inputs.models.access_esm1p6.generators.ghg._common import (
    GHG_MOLAR_MASS,
    cmip7_ghg_dirpath,
    cmip7_ghg_filename,
    cmip7_ghg_mmr,
    cmip7_pro_greg_date_constraint_from_years,
)

from cmip7_inputs.models.access_esm1p6.generators.ghg.series import (
    load_cmip7_ghg_series_mmr,
    cmip7_ghg_update_namelists_file,
)

# ------------------------------------------------------
# ------------------- PI CONTROL -----------------------
# ------------------------------------------------------

def load_cmip7_pi_ghg_mmr(args, ghg):
    '''
    Load the CMIP7 pre-industrial greenhouse gas mass mixing ratio for the given greenhouse gas.
    '''
    dirpath = cmip7_ghg_dirpath(args, "CMIP", ghg)
    filename = cmip7_ghg_filename(args, "CMIP", ghg)
    cmip7_filepath = dirpath / filename

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

    # Define the mapping from greenhouse gas names to namelist variable names
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
    # Patch the greenhouse gas variables in the RUN_Radiation namelist. Example: namelist_dict["CO2_MMR"] = ghg_mmr_dict["co2"]
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
    pi_ghg_namelist_filepath = Path("atmosphere") / "namelists"
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

@registry.register(
    model=MODEL_ID,
    input_name=input_names.GHG,
    experiments=[experiments.PI_CONTROL, experiments.TEST],
)
def generate_ghg_picontrol(request: GenerationRequest) :
    """Modify greenhouse gas namelist for:
    model: ACCESS-ESM1.6
    experiment: piControl

    Patch the greenhouse gas variables in the RUN_Radiation namelist
    """

    args = cmip7_parse_args(request)
    # Load the CMIP7 pre-industrial greenhouse gas mass mixing ratios for each greenhouse gas
    ghg_mmr_dict = dict()
    for ghg in GHG_MOLAR_MASS:
        ghg_mmr_dict[ghg] = load_cmip7_pi_ghg_mmr(args, ghg)

    # Patch the greenhouse gas variables in the RUN_Radiation namelist
    cmip7_pi_ghg_patch(ghg_mmr_dict)


# ------------------------------------------------------
# ------------------- HISTORICAL -----------------------
# ------------------------------------------------------

@registry.register(
    model=MODEL_ID,
    input_name=input_names.GHG,
    experiments=[experiments.HISTORICAL,],
)
def generate_ghg_historical(request: GenerationRequest):
    """Modify the namelists file to include the ghg namelist for:
    model: ACCESS-ESM1.6
    experiment: historical
    """
    args = cmip7_parse_args(request)

    ghg_mmr_dict = dict()
    for ghg in GHG_MOLAR_MASS:
        ghg_mmr_dict[ghg] = load_cmip7_ghg_series_mmr(
            args, "CMIP", ghg, CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR
        )

    # Patch the greenhouse gas namelist.
    cmip7_ghg_update_namelists_file(
        ghg_mmr_dict, CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR
    )

# ----------------------------------------------------------
# --------------------- SCENARIO MIP -----------------------
# ----------------------------------------------------------

