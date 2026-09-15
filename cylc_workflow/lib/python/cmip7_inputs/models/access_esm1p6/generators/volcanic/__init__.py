"""
ACCESS-ESM1.6 volcanic forcing generators.

Importing this package registers all of ACCESS-ESM1.6's volcanic
generators.

In here I compiled the cmip7_HI_volcanic_generate.py, cmip7_PI_volcanic_generate.py and cmip7_SM_volcanic_generate.py into one file.
"""
from __future__ import annotations

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.core.registry import registry
from cmip7_inputs.models.access_esm1p6 import MODEL_ID

from cmip7_inputs.models.access_esm1p6.generators._common import cmip7_parse_args

from cmip7_inputs.models.access_esm1p6.generators.volcanic._common import cmip7_volcanic_dirpath

from cmip7_inputs.models.access_esm1p6.generators.volcanic._picontrol import (
    cmip7_pi_volcanic_filename,
    average_stratospheric_aerosol_optical_depth,
    cmip7_pi_volcanic_patch,
)

from cmip7_inputs.models.access_esm1p6.generators.volcanic._historical import (
    cmip7_hi_volcanic_filename,
    save_hi_stratospheric_aerosol_optical_depth,
)

# TODO: Maybe historical and scenarioMIP should be combined into one function 
# with a parameter for the experiment type. 
# The only difference is the directory path and the years to save.

# These two are inputs from the CLI and are located in the variables.cylc file
#CMIP7_SOURCE_PATH = '/g/data/qv56/replicas/input4MIPs/CMIP7'
#ANCIL_TARGET_PATH = '/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil_test/'~ISO_DATE_TODAY

# ------------------------------------------------------
# ------------------- PI CONTROL -----------------------
# ------------------------------------------------------

@registry.register(
    model=MODEL_ID,
    input_name=input_names.VOLCANIC,
    experiments=[experiments.PI_CONTROL],
)
def generate_volcanic_picontrol(request: GenerationRequest) :
    """Modify volcanic namelist for:
    model: ACCESS-ESM1.6
    experiment: piControl

    Patch the VOLCTS_val variable in the coupling namelist
    """

    args = cmip7_parse_args(request)
    dirpath = cmip7_volcanic_dirpath(
        args, "CMIP", "monC", args.dataset_version, args.dataset_vdate,
    )
    filename = cmip7_pi_volcanic_filename(
        args.dataset_version, args.dataset_date_range,
    )
    dataset_path = dirpath / filename

    # Calculate the average stratospheric optical depth.
    average_saod = average_stratospheric_aerosol_optical_depth(dataset_path)

    # Patch the VOLCTS_val variable in the coupling namelist.
    cmip7_pi_volcanic_patch(average_saod)


# ------------------------------------------------------
# ------------------- HISTORICAL -----------------------
# ------------------------------------------------------
# cmip7-inputs -m access-esm1.6 -n solar -e historical -o output_test 
# -O dataset-version=SOLARIS-HEPPA-CMIP-4-6 -O dataset-vdate=v20250219 
# -O dataset-date-range=185001-202312 -O save-filename=TSI_CMIP7_ESM 
# -O cmip7-source-data-dirname=/input_test -O ancil_target_dirname=/ancil_dirname


@registry.register(
    model=MODEL_ID,
    input_name=input_names.VOLCANIC,
    experiments=[experiments.HISTORICAL],
)
def generate_volcanic_historical(request: GenerationRequest):
    """Generate volcanic forcing ancillary file for:
    model: ACCESS-ESM1.6
    experiment: historical
    """
    args = cmip7_parse_args(request)

    dirpath = cmip7_volcanic_dirpath(
        args, "CMIP", "mon", args.dataset_version, args.dataset_vdate,
    )
    filename = cmip7_hi_volcanic_filename(
        args.dataset_version, args.dataset_date_range,
    )
    dataset_path = dirpath / filename

    # Calculate and save the average stratospheric aerosol optical depth.
    save_hi_stratospheric_aerosol_optical_depth(args, dataset_path)

# ----------------------------------------------------------
# --------------------- SCENARIO MIP -----------------------
# ----------------------------------------------------------

