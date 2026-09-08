'''
CMIP7 anthropogenic aerosol emissions data loading and interpolation functions.
Anthropogenic aerosol emissions refers to aerosol emissions from human activities, such as industrial processes, transportation, and agriculture.

This module provides functions to load and interpolate CMIP7 anthropogenic aerosol emissions data to the ESM1.5 grid. 
The functions load the CMIP7 anthropogenic aerosol emissions data, 
aggregate the sector dimension by summing all sector contributions into a single field, 
and interpolate the data to the ESM1.5 grid using the specified interpolation scheme. 
The interpolated data is then saved to the specified directory path with the appropriate STASH item for the ESM1.5 model.
'''
from pathlib import Path

import iris
from aerosol.cmip7_aerosol_common import (
    load_cmip7_aerosol,
    load_cmip7_aerosol_list,
    zero_poles,
)
from cmip7_ancil_common import (
    INTERPOLATION_SCHEME,
    esm_grid_mask_cube,
    fix_coords,
    save_ancil,
)


def _anthro_dirpath(args, variable):
    '''
    Return the directory path to the CMIP7 anthropogenic aerosol emissions data for the given variable.'''
    return (
        Path(args.cmip7_source_data_dirname)
        / "CMIP"
        / "PNNL-JGCRI"
        / args.dataset_version
        / "atmos"
        / "mon"
        / variable
        / "gn"
        / args.dataset_vdate
    )


def cmip7_aerosol_air_anthro_filepath(args, species, date_range):
    '''
    Return the file path to the CMIP7 air anthropogenic aerosol emissions data for the given species and date range.   
    '''
    dirpath = _anthro_dirpath(args, f"{species}_em_AIR_anthro")
    filename = (
        f"{species}-em-AIR-anthro_input4MIPs_emissions_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def cmip7_aerosol_anthro_filepath(args, species, date_range):
    '''
    Return the file path to the CMIP7 anthropogenic aerosol emissions data for the given species and date range.   
    '''
    dirpath = _anthro_dirpath(args, f"{species}_em_anthro")
    filename = (
        f"{species}-em-anthro_input4MIPs_emissions_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def load_cmip7_aerosol_anthro(args, species, date_range, constraint):
    '''
    Load the CMIP7 anthropogenic aerosol emissions data for the given species and date range, and apply the given constraint.   
    '''
    # Load the CMIP7 anthropogenic aerosol emissions data
    cube = load_cmip7_aerosol(
        args, cmip7_aerosol_anthro_filepath, species, date_range, constraint
    )
    # Fix the coordinates of the cube to match the ESM1.5 grid
    fix_coords(args, cube)
    return cube


def load_cmip7_aerosol_air_anthro_list(
    args, species, date_range_list, constraint
):
    '''
    Load the CMIP7 anthropogenic aerosol air emissions data for the given species and date range list, and apply the given constraint.
    '''
    # Load the CMIP7 anthropogenic aerosol air emissions data
    cube = load_cmip7_aerosol_list(
        args,
        cmip7_aerosol_air_anthro_filepath,
        species,
        date_range_list,
        constraint,
    )
    # Fix the coordinates of the cube to match the ESM1.5 grid
    fix_coords(args, cube)
    return cube


def load_cmip7_aerosol_anthro_list(args, species, date_range_list, constraint):
    '''
    Load the CMIP7 anthropogenic aerosol emissions data for the given species and date range list, and apply the given constraint.
    '''
    # Load the CMIP7 anthropogenic aerosol air emissions data
    cube = load_cmip7_aerosol_list(
        args,
        cmip7_aerosol_anthro_filepath,
        species,
        date_range_list,
        constraint,
    )
    # Fix the coordinates of the cube to match the ESM1.5 grid
    fix_coords(args, cube)
    return cube


def cmip7_aerosol_anthro_interpolate(
    args, load_fn, species, stash_item, save_dirpath
):
    '''
    Interpolate CMIP7 anthropogenic aerosol emissions data to the ESM1.5 grid.
    '''
    cube = load_fn(args, species)
    # Aggregate the sector dimension by summing all sector contributions into a single field
    cube_tot = cube.collapsed(["sector"], iris.analysis.SUM)
    # Interpolate the CMIP7 anthropogenic aerosol emissions data to the ESM1.5 grid
    esm_cube = cube_tot.regrid(esm_grid_mask_cube(args), INTERPOLATION_SCHEME)
    # Fill the missing values with zeros and zero out the poles
    esm_cube.data = esm_cube.data.filled(0.0)
    zero_poles(esm_cube)
    # Set the STASH item for the output cube so that it can be correctly identified in the ESM1.5 model.
    esm_cube.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=stash_item
    )
    # Save the interpolated CMIP7 anthropogenic aerosol emissions data to the specified directory path
    save_ancil(esm_cube, save_dirpath, args.save_filename)
