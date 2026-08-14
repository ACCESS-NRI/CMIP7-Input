"""ACCESS-ESM1.6 solar forcing generators.

Importing this package registers all of ACCESS-ESM1.6's solar
generators.
"""

"""In here I compiled the cmip7_HI_solar_generate.py, cmip7_PI_solar_generate.py and cmip7_SM_solar_generate.py into one file."""

# TODO: Maybe historical and scenarioMIP should be combined into one function 
# with a parameter for the experiment type. 
# The only difference is the directory path and the years to save.

from __future__ import annotations

import f90nml

from pathlib import Path

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.core.registry import registry
from cmip7_inputs.models.access_esm1p6 import MODEL_ID

from cmip7_inputs.models.access_esm1p6.generators.solar._common import (
    write_mock_solar_file,
    cmip7_solar_dirpath,
    load_cmip7_solar_cube,
    cmip7_solar_save
)

from cmip7_inputs.models.access_esm1p6.generators._common_HI import (
    CMIP7_HI_BEG_YEAR,
    CMIP7_HI_END_YEAR,
    esm_hi_forcing_save_dirpath
)

from cmip7_inputs.models.access_esm1p6.generators._common_SM import esm_sm_forcing_save_dirpath

# These two are inputs from the CLI and are located in the variables.cylc file
#CMIP7_SOURCE_PATH = '/g/data/qv56/replicas/input4MIPs/CMIP7'
#ANCIL_TARGET_PATH = '/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil_test/'~ISO_DATE_TODAY

# ------------------------------------------------------
# ------------------- PI CONTROL -----------------------
# ------------------------------------------------------
@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[experiments.PI_CONTROL, experiments.TEST],
)
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

def generate_solar_picontrol(request: GenerationRequest) -> Path:
    """Generate solar forcing input file for:
    model: ACCESS-ESM1.6
    experiment: piControl

    Placeholder processing that writes a text file describing the
    request instead of real solar forcing data.
    """
    dirpath = cmip7_solar_dirpath(request, "CMIP", "fx")
    filename = f"multiple_input4MIPs_solar_CMIP_{request.options['dataset-version']}_gn.nc"
    dataset_path = dirpath / filename

    solar_irradiance_cube = load_cmip7_solar_cube(dataset_path)
    solar_irradiance = solar_irradiance_cube[0].data

    # Patch the SC variable in the coupling namelist
    cmip7_pi_solar_patch(solar_irradiance)

    return write_mock_solar_file(request)

# ------------------------------------------------------
# ------------------- HISTORICAL -----------------------
# ------------------------------------------------------
# cmip7-inputs -m access-esm1.6 -n solar -e historical -o output_test 
# -O dataset-version=SOLARIS-HEPPA-CMIP-4-6 -O dataset-vdate=v20250219 
# -O dataset-date-range=185001-202312 -O save-filename=TSI_CMIP7_ESM 
# -O cmip7-source-data-dirname=/input_test -O ancil_target_dirname=/ancil_dirname

def cmip7_hi_solar_save(request: GenerationRequest, cube):
    """
    Save the TSI values for each year into a text file.
    """
    save_dirpath = esm_hi_forcing_save_dirpath(request)
    cmip7_solar_save(
        request, cube, CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR, save_dirpath
    )

@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[experiments.HISTORICAL],
)
def generate_solar_historical(request: GenerationRequest) -> Path:
    """Generate solar forcing input file for:
    model: ACCESS-ESM1.6
    experiment: historical

    Placeholder processing that writes a text file describing the
    request instead of real solar forcing data.
    """
    dirpath = cmip7_solar_dirpath(request, "CMIP", "mon")

    filename = (
        "multiple_input4MIPs_solar_CMIP_"
        f"{request.options['dataset-version']}_gn_"
        f"{request.options['dataset-date-range']}.nc"
    )

    dataset_path = dirpath / filename

    solar_irradiance_cube = load_cmip7_solar_cube(dataset_path)

    cmip7_hi_solar_save(request, solar_irradiance_cube)

    return write_mock_solar_file(request,dirpath, dataset_path)

# ----------------------------------------------------------
# --------------------- SCENARIO MIP -----------------------
# ----------------------------------------------------------

# TODO: why are these years different from the common_SM.py years?
CMIP7_SM_SOLAR_BEG_YEAR = 2022
CMIP7_SM_SOLAR_END_YEAR = 2299

def cmip7_sm_solar_save(request: GenerationRequest, cube):
    """
    Save the TSI values for each year into a text file.
    """
    save_dirpath = esm_sm_forcing_save_dirpath(request)
    cmip7_solar_save(
        request,
        cube,
        CMIP7_SM_SOLAR_BEG_YEAR,
        CMIP7_SM_SOLAR_END_YEAR,
        save_dirpath,
    )

@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[experiments.SCENARIO_MIP],
)
def generate_solar_scenariomip(request: GenerationRequest) -> Path:
    """Generate solar forcing input file for:
    model: ACCESS-ESM1.6
    experiment: ScenarioMIP

    Placeholder processing that writes a text file describing the
    request instead of real solar forcing data.
    """

    dirpath = cmip7_solar_dirpath(request, "ScenarioMIP", "mon")
    filename = (
        "multiple_input4MIPs_solar_ScenarioMIP_"
        f"{request.options['dataset-version']}_gn_"
        f"{request.options['dataset-date-range']}.nc"
    )
    dataset_path = dirpath / filename

    solar_irradiance_cube = load_cmip7_solar_cube(dataset_path)

    cmip7_sm_solar_save(request, solar_irradiance_cube)

    return write_mock_solar_file(request)