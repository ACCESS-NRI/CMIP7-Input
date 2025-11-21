from argparse import ArgumentParser
from pathlib import Path

import iris
from iris.util import equalise_attributes

from ..cmip7_ancil_argparse import common_parser
from ..cmip7_ancil_common import (
    INTERPOLATION_SCHEME,
    esm_grid_mask_cube,
    fix_coords,
    save_ancil,
)
from ..cmip7_ancil_constants import ANCIL_TODAY
from .cmip7_nitrogen import (
    NITROGEN_SPECIES,
    NITROGEN_STASH_ITEM,
    cmip7_nitrogen_dirpath,
)


def parse_args():
    parser = ArgumentParser(
        parents=[common_parser()],
        prog="cmip7_PI_nitrogen_generate",
        description=(
            "Generate input files from CMIP7 pre-industrial nitrogen forcings"
        ),
    )
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_pi_nitrogen_filepath(args, species):
    dirpath = cmip7_nitrogen_dirpath(args, "monC", species)
    filename = (
        f"{species}_input4MIPs_surfaceFluxes_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}-clim.nc"
    )
    return dirpath / filename


def load_cmip7_pi_nitrogen_species(args, species):
    species_filepath = cmip7_pi_nitrogen_filepath(args, species)
    cube = iris.load_cube(species_filepath)
    return cube


def load_cmip7_pi_nitrogen(args):
    # Load all of the PI nitrogen datasets into a CubeList
    nitrogen_cubes = iris.cube.CubeList()
    for species in NITROGEN_SPECIES:
        species_cube = load_cmip7_pi_nitrogen_species(args, species)
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


def regrid_cmip7_pi_nitrogen(args, cube):
    # Make the coordinates comaptible with the ESM1.5 grid mask
    fix_coords(args, cube)
    # Regrid using the ESM1.5 grid mask
    esm_cube = cube.regrid(esm_grid_mask_cube(args), INTERPOLATION_SCHEME)
    esm_cube.data = esm_cube.data.filled(0.0)
    return esm_cube


def esm_pi_nitrogen_save_dirpath(args):
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


def save_cmip7_pi_nitrogen(args, cube):
    # Add STASH metadata
    cube.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=NITROGEN_STASH_ITEM
    )
    # Save as an ancillary file
    save_dirpath = esm_pi_nitrogen_save_dirpath(args)
    save_ancil(cube, save_dirpath, args.save_filename)


if __name__ == "__main__":
    args = parse_args()

    # Load the CMIP7 datasets
    nitrogen_cube = load_cmip7_pi_nitrogen(args)
    # Regrid to match the ESM1.5 mask
    esm_cube = regrid_cmip7_pi_nitrogen(args, nitrogen_cube)
    # Save the ancillary
    save_cmip7_pi_nitrogen(args, esm_cube)
