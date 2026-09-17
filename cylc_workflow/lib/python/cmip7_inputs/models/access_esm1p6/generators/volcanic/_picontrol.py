"""Shared helpers for ACCESS-ESM1.6 volcanic picontrol generators."""

from __future__ import annotations

import f90nml
import iris
from pathlib import Path
import numpy as np

<<<<<<< HEAD
from cmip7_inputs.models.access_esm1p6.generators._common_PI import (
    DAYS_IN_CMIP7_PI_YEAR
)

from cmip7_inputs.models.access_esm1p6.generators.volcanic._common import (
    SAOD_SCALING,
    SAOD_WAVELENGTH,
=======
from cmip7_inputs.models.access_esm1p6.generators.volcanic._common import (
>>>>>>> 846bfef (Add volcanic before testing)
    constrain_to_wavelength,
    mean_over_latitudes,
    sum_over_height_layers,
)

<<<<<<< HEAD
def cmip7_pi_volcanic_filename(dataset_version, dataset_date_range):
=======
from cmip7_inputs.models.access_esm1p6.generators._constants import (
    SAOD_SCALING,
    SAOD_WAVELENGTH,
    DAYS_IN_PI_YEAR
)

def get_pi_volcanic_filename(dataset_version, dataset_date_range):
>>>>>>> 846bfef (Add volcanic before testing)
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
<<<<<<< HEAD
        np.diff(np.append(time_coord.points, [DAYS_IN_CMIP7_PI_YEAR]))
        / DAYS_IN_CMIP7_PI_YEAR
=======
        np.diff(np.append(time_coord.points, [DAYS_IN_PI_YEAR]))
        / DAYS_IN_PI_YEAR
>>>>>>> 846bfef (Add volcanic before testing)
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


<<<<<<< HEAD
def cmip7_pi_volcanic_patch(average_saod):
=======
def patch_pi_volcanic(average_saod):
>>>>>>> 846bfef (Add volcanic before testing)
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
