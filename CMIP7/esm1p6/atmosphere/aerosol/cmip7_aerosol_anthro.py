import iris
import os
from aerosol.cmip7_aerosol_common import (
    load_cmip7_aerosol,
    load_cmip7_aerosol_list,
    zero_poles,
)
from cmip7_ancil_common import (
    INTERPOLATION_SCHEME,
    esm_grid_mask_cube,
    extend_years,
    fix_coords,
    save_ancil,
)
from cmip7_ancil_path_classes import Cmip7Filepath


cmip7_aerosol_anthro_dirname_template = os.path.join(
    "PNNL-JGCRI",
    "{version}",
    "atmos",
    "{period}",
    "{species}_em_anthro",
    "gn",
    "{vdate}"
)
cmip7_aerosol_anthro_filename_template = (
    "{species}-em-anthro_input4MIPs_emissions_CMIP_"
    "{version}_gn_{date_range}.nc"
)


def cmip7_aerosol_anthro_filepath(args, species, date_range):
    filepath = Cmip7Filepath(
        root_dirname=args.cmip7_source_data_dirname,
        dirname_template=cmip7_aerosol_anthro_dirname_template,
        filename_template=cmip7_aerosol_anthro_filename_template,
        version=args.dataset_version,
        vdate=args.dataset_vdate,
        period="mon",
        date_range=date_range,
        species=species
    )
    return filepath()


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
    cube_tot = cube.collapsed(["sector"], iris.analysis.SUM)
    esm_cube = cube_tot.regrid(esm_grid_mask_cube(args), INTERPOLATION_SCHEME)
    esm_cube.data = esm_cube.data.filled(0.0)
    zero_poles(esm_cube)
    esm_cube.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=stash_item
    )
    # Extend the historical time series, if any,
    # by duplicating the first and last years
    esm_cube = extend_years(esm_cube)
    save_ancil(esm_cube, save_dirpath, args.save_filename)
