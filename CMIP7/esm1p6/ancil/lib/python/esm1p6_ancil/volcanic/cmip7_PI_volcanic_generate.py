import os
from argparse import ArgumentParser
from pathlib import Path

import f90nml
import iris
import numpy as np
from cmip7_ancil_argparse import config_parser
from cmip7_PI import DAYS_IN_CMIP7_PI_YEAR
from dataset import DatasetConfig
from volcanic.cmip7_volcanic import (
    SAOD_SCALING,
    SAOD_WAVELENGTH,
    constrain_to_wavelength,
    mean_over_latitudes,
    sum_over_height_layers,
)


def parse_args():
    """Parse command-line arguments for pre-industrial volcanic forcing
    generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing dataset config and
            configuration directory.
    """
    parser = ArgumentParser(
        parents=[config_parser()],
        prog="cmip7_PI_volcanic_generate",
        description=(
            "Generate input files from CMIP7 pre-industrial volcanic forcings"
        ),
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path.cwd(),
        help="Path to configuration repository containing atmosphere/",
    )
    return parser.parse_args()


def mean_over_pi_months(cube):
    """Find the time average SAOD by averaging over months
    in the pre-industrial year, weighted by month length.

    Args:
        cube (iris.cube.Cube): Climatological 12-month volcanic extinction
            cube.

    Returns:
        iris.cube.Cube: Collapsed single-slice cube averaged over the 12
            calendar months.
    """
    time_coord = next(c for c in cube.coords() if c.standard_name == "time")
    # Iris emits a UserWarning when collapsing unbounded coordinates;
    # guessing bounds silences the warning without altering the weighted mean.
    if not time_coord.has_bounds():
        time_coord.guess_bounds()
    time_weights = (
        np.diff(np.append(time_coord.points, [DAYS_IN_CMIP7_PI_YEAR]))
        / DAYS_IN_CMIP7_PI_YEAR
    )
    return cube.collapsed(["time"], iris.analysis.MEAN, weights=time_weights)


def average_stratospheric_aerosol_optical_depth(dataset_path):
    """Calculate the average stratospheric optical depth (SAOD)
    by averaging extinction over both time and latitude,
    and summing over stratospheric layers.

    Args:
        dataset_path (os.PathLike): Path to the climatological volcanic
            extinction dataset.

    Returns:
        float or numpy.ndarray: Globally averaged, vertically integrated SAOD
            value.
    """
    # Load the dataset into an Iris cube.
    cube = iris.load_cube(os.fspath(dataset_path))

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


def cmip7_pi_volcanic_patch(average_saod, config_dir):
    """Patch the VOLCTS_val variable in the coupling namelist.

    Args:
        average_saod (float): Unscaled pre-industrial average SAOD (scaled by
            SAOD_SCALING inside).
        config_dir (pathlib.Path): Configuration repository directory.
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
    pi_volcanic_namelist_filepath = config_dir / "atmosphere" / "input_atm.nml"
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

    config = DatasetConfig.from_yaml(args.config)
    dataset = config.to_dataset()

    # Calculate the average stratospheric optical depth.
    average_saod = average_stratospheric_aerosol_optical_depth(dataset)

    # Patch the VOLCTS_val variable in the coupling namelist.
    cmip7_pi_volcanic_patch(average_saod, args.config_dir)
