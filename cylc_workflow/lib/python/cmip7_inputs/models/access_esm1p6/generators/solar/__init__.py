"""ACCESS-ESM1.6 solar forcing generators.

Importing this package registers all of ACCESS-ESM1.6's solar
generators.
"""

from __future__ import annotations

from pathlib import Path
import f90nml

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.core.registry import registry
from cmip7_inputs.models.access_esm1p6 import MODEL_ID

from cmip7_inputs.models.access_esm1p6.generators._common import parse_additional_args

from cmip7_inputs.models.access_esm1p6.generators.solar._common import (
    get_solar_dirpath,
    load_solar_cube
)

from cmip7_inputs.models.access_esm1p6.generators.solar._historical import save_historical_solar

# ------------------------------------------------------
# ------------------- HISTORICAL -----------------------
# ------------------------------------------------------
# cmip7-inputs -m access-esm1.6 -n solar -e historical -o output_test 
# -O dataset-version=SOLARIS-HEPPA-CMIP-4-6 -O dataset-vdate=v20250219 
# -O dataset-date-range=185001-202312 -O save-filename=TSI_CMIP7_ESM 
# -O cmip7-source-data-dirname=/input_test -O ancil_target_dirname=/ancil_dirname

@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[experiments.HISTORICAL,],
)
def generate_solar_historical(request: GenerationRequest):
    """Generate solar forcing input file for:
    model: ACCESS-ESM1.6
    experiment: historical
    """
    args = parse_additional_args(request)

    dirpath = get_solar_dirpath(args, "CMIP", "mon")
    filename = (
        "multiple_input4MIPs_solar_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}.nc"
    )
    dataset_path = dirpath / filename

    solar_irradiance_cube = load_solar_cube(dataset_path)

    save_historical_solar(request.output_dir, args, solar_irradiance_cube)

# ------------------------------------------------------
# ------------------- PI CONTROL -----------------------
# ------------------------------------------------------

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

@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[experiments.PI_CONTROL],
)
def generate_solar_picontrol(request: GenerationRequest) :
    """Modify solar forcing namelist for:
    model: ACCESS-ESM1.6
    experiment: piControl

    Placeholder processing that writes a text file describing the
    request instead of real solar forcing data.
    """

    args = cmip7_parse_args(request)
    dirpath = cmip7_solar_dirpath(args, "CMIP", "fx")
    filename = f"multiple_input4MIPs_solar_CMIP_{args.dataset_version}_gn.nc"
    dataset_path = dirpath / filename

    solar_irradiance_cube = load_cmip7_solar_cube(dataset_path)
    solar_irradiance = solar_irradiance_cube[0].data

    # Patch the SC variable in the coupling namelist
    cmip7_pi_solar_patch(solar_irradiance)
