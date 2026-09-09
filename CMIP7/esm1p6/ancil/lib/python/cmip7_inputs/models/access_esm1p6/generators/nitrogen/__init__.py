"""
ACCESS-ESM1.6 nitrogen forcing generators.

Importing this package registers all of ACCESS-ESM1.6's nitrogen
generators.

In here I compiled the cmip7_HI_nitrogen_generate.py, cmip7_PI_nitrogen_generate.py and cmip7_SM_nitrogen_generate.py into one file.
"""
from __future__ import annotations

from pathlib import Path

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.core.registry import registry
from cmip7_inputs.models.access_esm1p6 import MODEL_ID

from cmip7_inputs.models.access_esm1p6.generators._constants import ANCIL_TODAY

from cmip7_inputs.models.access_esm1p6.generators._common import (
    cmip7_parse_args,
    extend_years
)

from cmip7_inputs.models.access_esm1p6.generators.nitrogen._common import (
    cmip7_nitrogen_dirpath,
    save_cmip7_nitrogen,
    load_cmip7_nitrogen,
    regrid_cmip7_nitrogen,
)


# These two are inputs from the CLI and are located in the variables.cylc file
#CMIP7_SOURCE_PATH = '/g/data/qv56/replicas/input4MIPs/CMIP7'
#ANCIL_TARGET_PATH = '/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil_test/'~ISO_DATE_TODAY

# ------------------------------------------------------
# ------------------- PI CONTROL -----------------------
# ------------------------------------------------------

# TODO: Is this function really needed? There are other functions that do the same thing, but with different names. Maybe we can unify them.
# Like cmip7_sm_nitrogen_filepath
def cmip7_pi_nitrogen_filepath(args, species):
    '''
    Return the file path to the CMIP7 pre-industrial nitrogen dataset for the given species.'''
    dirpath = cmip7_nitrogen_dirpath(args, "CMIP", "monC", species)
    filename = (
        f"{species}_input4MIPs_surfaceFluxes_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}-clim.nc"
    )
    return dirpath / filename


def esm_pi_nitrogen_save_dirpath(args):
    '''
    Return the directory path to save the ESM1.5 pre-industrial nitrogen ancil file.
    '''
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "pre-industrial"
        / "atmosphere"
        / "land"
        / "biogeochemistry"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )

@registry.register(
    model=MODEL_ID,
    input_name=input_names.NITROGEN,
    experiments=[experiments.PI_CONTROL],
)
def generate_nitrogen_picontrol(request: GenerationRequest) :
    """Modify nitrogen namelist for:
    model: ACCESS-ESM1.6
    experiment: piControl
    """

    args = cmip7_parse_args(request)
    # Load the CMIP7 datasets
    nitrogen_cube = load_cmip7_nitrogen(args, cmip7_pi_nitrogen_filepath)
    # Regrid to match the ESM1.5 mask
    esm_cube = regrid_cmip7_nitrogen(args, nitrogen_cube)
    # Save the ancillary
    save_cmip7_nitrogen(args, esm_cube, esm_pi_nitrogen_save_dirpath)


# ------------------------------------------------------
# ------------------- HISTORICAL -----------------------
# ------------------------------------------------------
# cmip7-inputs -m access-esm1.6 -n solar -e historical -o output_test 
# -O dataset-version=SOLARIS-HEPPA-CMIP-4-6 -O dataset-vdate=v20250219 
# -O dataset-date-range=185001-202312 -O save-filename=TSI_CMIP7_ESM 
# -O cmip7-source-data-dirname=/input_test -O ancil_target_dirname=/ancil_dirname

# TODO: Is this function really needed? There are other functions that do the same thing, but with different names. Maybe we can unify them.
# Like cmip7_pi_nitrogen_filepath AND cmip7_sm_nitrogen_filepath
def cmip7_hi_nitrogen_filepath(args, species):
    '''
    Return the file path to the CMIP7 historical nitrogen dataset for the given species.
    '''
    dirpath = cmip7_nitrogen_dirpath(args, "CMIP", "mon", species)
    filename = (
        f"{species}_input4MIPs_surfaceFluxes_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}.nc"
    )
    return dirpath / filename


def esm_hi_nitrogen_save_dirpath(args):
    '''
    Return the directory path to save the ESM1.5 historical nitrogen ancil file.
    '''
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "historical"
        / "atmosphere"
        / "land"
        / "biogeochemistry"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )

@registry.register(
    model=MODEL_ID,
    input_name=input_names.NITROGEN,
    experiments=[experiments.HISTORICAL],
)
def generate_nitrogen_historical(request: GenerationRequest):
    """Generate nitrogen forcing ancillary file for:
    model: ACCESS-ESM1.6
    experiment: historical
    """
    args = cmip7_parse_args(request)

    # Load the CMIP7 datasets
    nitrogen_cube = load_cmip7_nitrogen(args, cmip7_hi_nitrogen_filepath)
    # Regrid to match the ESM1.5 mask and extend the time series
    esm_cube = extend_years(regrid_cmip7_nitrogen(args, nitrogen_cube))
    # Save the ancillary
    save_cmip7_nitrogen(args, esm_cube, esm_hi_nitrogen_save_dirpath)

# ----------------------------------------------------------
# --------------------- SCENARIO MIP -----------------------
# ----------------------------------------------------------

