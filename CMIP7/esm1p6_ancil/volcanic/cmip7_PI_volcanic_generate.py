from argparse import ArgumentParser
from pathlib import Path

import f90nml
import iris
import numpy as np
from esm1p6_ancil.cmip7_ancil_argparse import dataset_parser, path_parser
from esm1p6_ancil.cmip7_PI import DAYS_IN_CMIP7_PI_YEAR
from esm1p6_ancil.volcanic.cmip7_volcanic import (
    SAOD_WAVELENGTH,
    cmip7_volcanic_dirpath,
    constrain_to_wavelength,
    mean_over_latitudes,
    sum_over_height_layers,
)


def parse_args():
    parser = ArgumentParser(
        parents=[path_parser(), dataset_parser()],
        prog="cmip7_PI_volcanic_generate",
        description=(
            "Generate input files from CMIP7 pre-industrial volcanic forcings"
        ),
    )
    parser.add_argument("--dataset-date-range")
    return parser.parse_args()


def cmip7_pi_volcanic_filename(args):
    return (
        f"ext_input4MIPs_aerosolProperties_CMIP_"
        f"{args.dataset_version}_gnz_"
        f"{args.dataset_date_range}-clim.nc"
    )


def mean_over_pi_months(cube):
    """
    Find the time average SAOD by averaging over months
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
    namelist_dict["VOLCTS_val"] = average_saod * 10000.0
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


if __name__ == "__main__":
    args = parse_args()

    dataset_path = cmip7_volcanic_dirpath(
        args, period="monC"
    ) / cmip7_pi_volcanic_filename(args)

    # Calculate the average stratospheric optical depth.
    average_saod = average_stratospheric_aerosol_optical_depth(dataset_path)

    # Patch the VOLCTS_val variable in the coupling namelist.
    cmip7_pi_volcanic_patch(average_saod)
