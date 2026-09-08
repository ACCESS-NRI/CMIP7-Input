'''
This module provides functions to load and fix the CMIP7 ozone ancillary file for use with the ESM1.5 model.
The functions in this module are used to load the CMIP7 ozone data from a NetCDF file, fix the coordinates to match the ESM1.5 grid, and return the resulting iris cube. 
The module also provides functions to parse command line arguments for the input and output file paths, as well as the grid information. 
The module is designed to be used in conjunction with other scripts that generate the CMIP7 ozone ancillary files for different scenarios, such as historical, pre-industrial, and ScenarioMIP. 
The output is saved in a specified directory with a filename provided by the user
'''

from argparse import ArgumentParser
from pathlib import Path

import iris
from cmip7_ancil_common import fix_coords

# TODO: This is the exact same parser as in cmip7_ancil_ukesm.py. Consider refactoring to avoid code duplication.
def ozone_parser():
    """
    Return an ArgumentParser for CMIP7 ozone ancil file processing.
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--ukesm-ancil-dirpath")
    parser.add_argument("--ukesm-netcdf-filename")
    parser.add_argument("--save-filename")
    return parser

# TODO: This is the exact same function as in cmip7_ancil_ukesm.py. Consider refactoring to avoid code duplication.
def cmip7_ozone_filepath(args):
    '''
    Return the file path to the CMIP7 ozone ancil file.
    '''
    dirpath = Path(args.ukesm_ancil_dirpath)
    filename = args.ukesm_netcdf_filename
    return dirpath / filename

# TODO: This is the exact same function as in cmip7_ancil_ukesm.py. Consider refactoring to avoid code duplication.
def load_cmip7_ozone(args):
    """
    Load the CMIP7 ozone ancil file as an iris cube.
    """
    filepath = cmip7_ozone_filepath(args)
    cube = iris.load_cube(filepath)
    return cube

# TODO: This is the exact same function as in cmip7_ancil_ukesm.py. Except for the fix_poles() call and the fill parameter. Consider refactoring to avoid code duplication.
def fix_cmip7_ozone(args, cube):
    """
    Fix the coordinates of the CMIP7 ozone cube to be compatible with the ESM1.5 (ESM1.6?) grid.
    """
    # Make the coordinates compatible with the ESM1.5 grid mask
    fix_coords(args, cube)
    # Replace any missing or invalid values with 0.0 to avoid issues with the ESM1.5 model
    cube.data = cube.data.filled(0.0)
    return cube
