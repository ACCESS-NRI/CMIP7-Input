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


def cmip7_aerosol_anthro_rootpath(args):
    return (
        Path(args.cmip7_source_data_dirname)
        / 'PNNL-JGCRI'
        / args.dataset_version
        / 'atmos'
        / 'mon'
    )


def cmip7_aerosol_anthro_filepath(args, species, date_range):
    rootpath = cmip7_aerosol_anthro_rootpath(args)
    filename = (
        f'{species}-em-anthro_input4MIPs_emissions_CMIP_'
        f'{args.dataset_version}_gn_'
        f'{date_range}.nc'
    )
    return (
        rootpath / f'{species}_em_anthro' / 'gn' / args.dataset_vdate / filename
    )


def cmip7_aerosol_anthro_filepath_list(args, species, date_range_list):
    return [
        cmip7_aerosol_anthro_filepath(args, species, date_range)
        for date_range in date_range_list
    ]


def load_cmip7_aerosol_anthro(args, species, date_range, constraint):
    cube = load_cmip7_aerosol(
        args, cmip7_aerosol_anthro_filepath, species, date_range, constraint
    )
    fix_coords(args, cube)
    return cube


def load_cmip7_aerosol_anthro_list(args, species, date_range_list, constraint):
    cube = load_cmip7_aerosol_list(
        args,
        cmip7_aerosol_anthro_filepath_list,
        species,
        date_range_list,
        constraint,
    )
    fix_coords(args, cube)
    return cube


def cmip7_aerosol_anthro_interpolate(
    args, load_fn, species, stash_item, save_dirpath
):
    cube = load_fn(args, species)
    cube_tot = cube.collapsed(['sector'], iris.analysis.SUM)
    esm_cube = cube_tot.regrid(esm_grid_mask_cube(args), INTERPOLATION_SCHEME)
    esm_cube.data = esm_cube.data.filled(0.0)
    zero_poles(esm_cube)
    esm_cube.attributes['STASH'] = iris.fileformats.pp.STASH(
        model=1, section=0, item=stash_item
    )
    save_ancil(esm_cube, save_dirpath, args.save_filename)
