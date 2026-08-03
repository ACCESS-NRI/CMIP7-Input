'''
CMIP7 nitrogen ancil file generation functions.
The functions load the CMIP7 nitrogen datasets, regrid them to the ESM1.5 grid, and save the resulting data as ancillary files.
'''
from pathlib import Path

import iris
from cmip7_ancil_common import (
    INTERPOLATION_SCHEME,
    esm_grid_mask_cube,
    fix_coords,
    save_ancil,
)
from iris.util import equalise_attributes

NITROGEN_SPECIES = ("drynhx", "drynoy", "wetnhx", "wetnoy")
"""
The STASH code to use is m01s00i884 NITROGEN DEPOSITION as per
https://github.com/ACCESS-NRI/access-esm1.6-configs/blob/dev-preindustrial%2Bconcentrations/atmosphere/prefix.PRESM_A#L711
"""
NITROGEN_STASH_ITEM = 884


def cmip7_nitrogen_dirpath(args, activity, period, species):
    '''
    Return the directory path to the CMIP7 nitrogen dataset for the given period and species.'''
    return (
        Path(args.cmip7_source_data_dirname)
        / activity
        / "FZJ"
        / args.dataset_version
        / "atmos"
        / period
        / species
        / "gn"
        / args.dataset_vdate
    )


def load_cmip7_nitrogen(args, load_filepath_fn):
    '''
    Load all of the CMIP7 nitrogen datasets into a single cube.
    '''
    # Load all of the PI nitrogen datasets into a CubeList
    nitrogen_cubes = iris.cube.CubeList()
    for species in NITROGEN_SPECIES:
        species_filepath = load_filepath_fn(args, species)
        species_cube = iris.load_cube(species_filepath)
        nitrogen_cubes.append(species_cube)
    # Remove all attributes that differ between cubes
    equalise_attributes(nitrogen_cubes)
    # Add the cubes together
    cube_tot = nitrogen_cubes[0]
    for cube in nitrogen_cubes[1:]:
        cube_tot += cube
    # Change the units from kg m-2 s-1 to g m-2 day-1
    cube_tot.convert_units("g m-2 day-1")
    return cube_tot


def regrid_cmip7_nitrogen(args, cube):
    '''
    Regrid the CMIP7 nitrogen data to the ESM1.5 grid.
    '''
    # Make the coordinates comaptible with the ESM1.5 grid mask
    fix_coords(args, cube)
    # Regrid using the ESM1.5 grid mask
    esm_cube = cube.regrid(esm_grid_mask_cube(args), INTERPOLATION_SCHEME)
    # Replace invalid values with 0.0 to avoid issues with the ESM1.5 model
    esm_cube.data = esm_cube.data.filled(0.0)
    return esm_cube


def save_cmip7_nitrogen(args, cube, save_dirpath_fn):
    # Add STASH metadata
    cube.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=NITROGEN_STASH_ITEM
    )
    # Save as an ancillary file
    save_dirpath = save_dirpath_fn(args)
    save_ancil(cube, save_dirpath, args.save_filename)
