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
    """Construct the source directory path for anthropogenic aerosol emission
    datasets.

    Args:
        args (argparse.Namespace): Command-line arguments containing dataset
            configuration.
        variable (str): Emission variable name (e.g. 'BC_em_anthro',
            'BC_em_AIR_anthro').

    Returns:
        pathlib.Path: Source directory path under CMIP/PNNL-
            JGCRI/{dataset_version}/atmos/mon/{variable}/gn/{dataset_vdate}.
    """
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
    """Construct the file path for aircraft anthropogenic aerosol emission
    netCDF files.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        date_range (str): Date range string.

    Returns:
        pathlib.Path: Path to the aircraft emissions netCDF file.
    """
    dirpath = _anthro_dirpath(args, f"{species}_em_AIR_anthro")
    filename = (
        f"{species}-em-AIR-anthro_input4MIPs_emissions_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def cmip7_aerosol_anthro_filepath(args, species, date_range):
    """Construct the file path for surface anthropogenic aerosol emission
    netCDF files.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        date_range (str): Date range string.

    Returns:
        pathlib.Path: Path to the surface emissions netCDF file.
    """
    dirpath = _anthro_dirpath(args, f"{species}_em_anthro")
    filename = (
        f"{species}-em-anthro_input4MIPs_emissions_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def load_cmip7_aerosol_anthro(args, species, date_range, constraint):
    """Load a surface anthropogenic aerosol emissions cube and harmonize
    coordinate metadata.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        date_range (str): Date range string.
        constraint (iris.Constraint or None): Coordinate or temporal
            constraint.

    Returns:
        iris.cube.Cube: Loaded and coordinate-harmonized Iris cube.
    """
    cube = load_cmip7_aerosol(
        args, cmip7_aerosol_anthro_filepath, species, date_range, constraint
    )
    fix_coords(args, cube)
    return cube


def load_cmip7_aerosol_air_anthro_list(
    args, species, date_range_list, constraint
):
    """Load, concatenate, and vertically integrate aircraft anthropogenic
    aerosol emissions.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        date_range_list (list of str): List of date range strings.
        constraint (iris.Constraint or None): Loading constraint.

    Returns:
        iris.cube.Cube: Concatenated and altitude-collapsed Iris cube.
    """
    cube = load_cmip7_aerosol_list(
        args,
        cmip7_aerosol_air_anthro_filepath,
        species,
        date_range_list,
        constraint,
    )
    fix_coords(args, cube)
    if cube.coords("altitude"):
        cube = cube.collapsed(["altitude"], iris.analysis.SUM)
        cube.remove_coord("altitude")
    return cube


def load_cmip7_aerosol_anthro_list(args, species, date_range_list, constraint):
    """Load, concatenate, and harmonize surface anthropogenic aerosol emissions
    across multiple files.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        date_range_list (list of str): List of date range strings.
        constraint (iris.Constraint or None): Loading constraint.

    Returns:
        iris.cube.Cube: Concatenated and coordinate-harmonized Iris cube.
    """
    cube = load_cmip7_aerosol_list(
        args,
        cmip7_aerosol_anthro_filepath,
        species,
        date_range_list,
        constraint,
    )
    fix_coords(args, cube)
    return cube


def cmip7_aerosol_anthro_interpolate(
    args, load_fn, species, stash_item, save_dirpath
):
    """Regrid sector-collapsed anthropogenic aerosol emissions to the ESM grid
    and save ancillary.

    Collapses sectors via summation, regrids horizontally with conservative
    area-weighting,
    zeroes polar rows, attaches the specified UM STASH item, and writes the
    ancillary file.

    Args:
        args (argparse.Namespace): Command-line arguments.
        load_fn (callable): Function returning an Iris cube given (args,
            species).
        species (str): Aerosol species name.
        stash_item (int): UM STASH item number.
        save_dirpath (pathlib.Path): Destination directory for the ancillary
            file.
    """
    cube = load_fn(args, species)
    cube_tot = cube.collapsed(["sector"], iris.analysis.SUM)
    esm_cube = cube_tot.regrid(esm_grid_mask_cube(args), INTERPOLATION_SCHEME)
    esm_cube.data = esm_cube.data.filled(0.0)
    zero_poles(esm_cube)
    esm_cube.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=stash_item
    )
    save_ancil(esm_cube, save_dirpath, args.save_filename)
