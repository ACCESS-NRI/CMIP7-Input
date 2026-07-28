'''
This script generates the CMIP7 pre-industrial mean ozone ancillary file. It loads the CMIP7 historical ozone data, computes the 21-year mean for each month, fixes the coordinates to match the ESM1.5 grid, and saves the result as an ancillary file.
The script uses the argparse module to parse command line arguments, including the paths to the input and output files, and the grid information. It also uses the iris library to manipulate the data cubes. 
The script defines several functions to handle the different steps of the process, including parsing arguments, loading the data, fixing the coordinates, and saving the output. The main block of the script calls these functions in sequence to perform the complete process.
The script is designed to be run from the command line, and it expects the user to provide the necessary arguments for the input and output file paths, as well as the grid information. 
The output is saved in a specified directory with a filename provided by the user.
'''

from argparse import ArgumentParser
from pathlib import Path

import iris.coord_categorisation
from cmip7_ancil_argparse import (
    grid_parser,
    path_parser,
)
from cmip7_ancil_common import save_ancil
from cmip7_ancil_constants import ANCIL_TODAY
from ozone.cmip7_ozone import (
    fix_cmip7_ozone,
    load_cmip7_ozone,
    ozone_parser,
)


def parse_args():
    '''
    Parse the command line arguments for CMIP7 pre-industrial mean ozone ancil file generation.
    '''
    parser = ArgumentParser(
        parents=[path_parser(), grid_parser(), ozone_parser()],
        prog="cmip7_PI_mean_ozone_generate",
        description=(
            "Generate input files from 21 year mean of UK CMIP7 historical"
            "ozone forcings"
        ),
    )
    return parser.parse_args()


def esm_pi_ozone_save_dirpath(args):
    '''
    Return the directory path to save the ESM1.5 pre-industrial mean ozone ancil file.
    '''
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "pre-industrial-mean"
        / "atmosphere"
        / "forcing"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


def save_cmip7_pi_mean_ozone(args, cube):
    '''
    Save the CMIP7 pre-industrial mean ozone cube as an ancillary file.
    The cube is first aggregated by month to compute the 21-year mean for each month, and then saved as an ancillary file.
    '''
    # Add a "month_number" variable.
    iris.coord_categorisation.add_month_number(
        cube, "time", name="month_number"
    )
    # Aggregate by "month_number" to obtain a mean for each month.
    cube = cube.aggregated_by("month_number", iris.analysis.MEAN)
    # Re-create the time bounds to ensure that time is contiguous.
    time = cube.coord("time")
    time.bounds = None
    # Set the time bounds so the coordinate value is halfway through the interval.
    time.guess_bounds(bound_position=0.5) 
    # Remove the added "month_number" coordinate before saving.
    cube.remove_coord("month_number")
    # Save as an ancillary file
    save_dirpath = esm_pi_ozone_save_dirpath(args)
    save_ancil(cube, save_dirpath, args.save_filename, replace_bounds=True)


if __name__ == "__main__":
    '''
    Generate the CMIP7 pre-industrial mean ozone ancillary file.
    '''
    args = parse_args()

    # Load the CMIP7 datasets
    ozone_cube = load_cmip7_ozone(args)
    # Match the ESM1.5 mask
    esm_cube = fix_cmip7_ozone(args, ozone_cube)
    # Save the ancillary
    save_cmip7_pi_mean_ozone(args, esm_cube)
