"""
ACCESS-ESM1.6 volcanic forcing generators.

Importing this package registers all of ACCESS-ESM1.6's volcanic
generators.

In here I compiled the cmip7_HI_volcanic_generate.py, cmip7_PI_volcanic_generate.py and cmip7_SM_volcanic_generate.py into one file.
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
from cmip7_inputs.models.access_esm1p6.generators._common_HI import esm_hi_forcing_save_dirpath
from cmip7_inputs.models.access_esm1p6.generators._common_PI import (
    DAYS_IN_CMIP7_PI_YEAR
)
from cmip7_inputs.models.access_esm1p6.generators._common_SM import esm_sm_forcing_save_dirpath

from cmip7_inputs.models.access_esm1p6.generators.volcanic._common import (
    cmip7_volcanic_dirpath,
    save_stratospheric_aerosol_optical_depth,
    SAOD_SCALING,
    SAOD_WAVELENGTH,
    cmip7_volcanic_dirpath,
    constrain_to_wavelength,
    mean_over_latitudes,
    sum_over_height_layers,
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

def cmip7_pi_volcanic_filename(dataset_version, dataset_date_range):
    '''
    Return the filename for the CMIP7 pre-industrial volcanic ancil file.
    '''
    return (
        f"ext_input4MIPs_aerosolProperties_CMIP_"
        f"{dataset_version}_gnz_"
        f"{dataset_date_range}-clim.nc"
    )

def mean_over_pi_months(cube):
    """
    Find the time average average stratospheric optical depth (SAOD) by averaging over months
    in the pre-industrial year, weighted by month length.
    """
    time_coord = next(c for c in cube.coords() if c.standard_name == "time")
    time_weights = (
        np.diff(np.append(time_coord.points, [DAYS_IN_CMIP7_PI_YEAR]))
        / DAYS_IN_CMIP7_PI_YEAR
    )
    return cube.collapsed(["time"], iris.analysis.MEAN, weights=time_weights)


def average_stratospheric_aerosol_optical_depth(dataset_path):
    """
    Calculate the average stratospheric optical depth (SAOD)
    by averaging extinction over both time and latitude,
    and summing over stratospheric layers.
    """
    # Load the dataset into an Iris cube.
    cube = iris.load_cube(dataset_path)

    # Constrain to just the CMIP7 prescribed wavelength.
    cube = constrain_to_wavelength(cube, SAOD_WAVELENGTH)

    # Replace NaN values with 0.
    np.nan_to_num(cube.data, copy=False)

    # Average over months in the pre-industrial year,
    # weighted by month length.
    cube = mean_over_pi_months(cube)

    # Find the mean over all latitude bands, weighted by area.
    cube = mean_over_latitudes(cube)

    # Calculate the stratospheric aerosol optical depth by
    # summing over stratospheric layers, weighted by layer height.
    cube = sum_over_height_layers(cube)

    return cube.data


def cmip7_pi_volcanic_patch(average_saod):
    """
    Patch the VOLCTS_val variable in the coupling namelist
    """
    namelist_dict = dict()
    namelist_dict["VOLCTS_val"] = average_saod * SAOD_SCALING
    patch = {"coupling": namelist_dict}
    patch_namelist = f90nml.namelist.Namelist(patch)
    # Set the floating point format to the right value
    patch_namelist.float_format = "6.2f"
    # The floating point format is ignored unless
    # you print the namelist or convert it to a string
    patch_str = str(patch_namelist)
    parser = f90nml.Parser()
    patch_str_namelist = parser.reads(patch_str)

    # Create a new namelist by patching the original namelist.
    pi_volcanic_namelist_filepath = Path("atmosphere") / "input_atm.nml"
    if not pi_volcanic_namelist_filepath.exists():
        raise FileNotFoundError(
            f"Namelist file {pi_volcanic_namelist_filepath} does not exist"
        )
    new_namelist_filepath = pi_volcanic_namelist_filepath.with_suffix(
        ".nml.patched"
    )
    parser.read(
        pi_volcanic_namelist_filepath, patch_str_namelist, new_namelist_filepath
    )

    # Replace the original namelist.
    new_namelist_filepath.replace(pi_volcanic_namelist_filepath)

@registry.register(
    model=MODEL_ID,
    input_name=input_names.VOLCANIC,
    experiments=[experiments.PI_CONTROL, experiments.TEST],
)
def generate_solar_picontrol(request: GenerationRequest) :
    """Generate volcanic forcing input file for:
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

# TODO: Are these the same as the cmip7_HI_BEG_YEAR and cmip7_HI_END_YEAR? If so, we should use those instead of duplicating the values here.
CMIP7_HI_VOLCANIC_BEG_YEAR = 1850
CMIP7_HI_VOLCANIC_END_YEAR = 2023


def cmip7_hi_volcanic_filename(dataset_version, dataset_date_range):
    '''
    Return the filename for the CMIP7 historical volcanic ancil file.
    '''
    return (
        f"ext_input4MIPs_aerosolProperties_CMIP_"
        f"{dataset_version}_gnz_"
        f"{dataset_date_range}.nc"
    )

#  TODO: Is this function really needed?
def save_hi_stratospheric_aerosol_optical_depth(args, dataset_path):
    """
    Calculate the average stratospheric aerosol optical depth (SAOD)
    for each historical month by averaging extinction over latitude,
    and summing over stratospheric layers. Save to the save file.
    """
    save_stratospheric_aerosol_optical_depth(
        args,
        CMIP7_HI_VOLCANIC_BEG_YEAR,
        CMIP7_HI_VOLCANIC_END_YEAR,
        dataset_path,
        esm_hi_forcing_save_dirpath(args),
    )


@registry.register(
    model=MODEL_ID,
    input_name=input_names.VOLCANIC,
    experiments=[experiments.HISTORICAL,],
)
def generate_solar_historical(request: GenerationRequest):
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

