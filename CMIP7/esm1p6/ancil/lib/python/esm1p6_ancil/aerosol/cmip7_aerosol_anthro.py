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


def anthro_variable(species, aircraft=False):
    """Return the DRS variable_id of an anthropogenic emissions dataset.

    Args:
        species (str): Emission species name (e.g. 'BC', 'OC', 'SO2').
        aircraft (bool, optional): Whether to name the aircraft emissions
            variable instead of the surface one. Defaults to False.

    Returns:
        str: Variable name, e.g. 'BC_em_anthro' or 'BC_em_AIR_anthro'.
    """
    infix = "_AIR" if aircraft else ""
    return f"{species}_em{infix}_anthro"


def load_cmip7_aerosol_anthro(args, config, species, constraint):
    """Load a surface anthropogenic aerosol emissions cube and harmonize
    coordinate metadata.

    Args:
        args (argparse.Namespace): Command-line arguments.
        config (dataset.DatasetConfig): Configuration of the surface
            emissions dataset, with a single time range.
        species (str): Aerosol species name.
        constraint (iris.Constraint or None): Coordinate or temporal
            constraint.

    Returns:
        iris.cube.Cube: Loaded and coordinate-harmonized Iris cube.
    """
    dataset = config.to_dataset(variable_id=anthro_variable(species))
    cube = load_cmip7_aerosol(dataset, constraint)
    fix_coords(args, cube)
    return cube


def load_cmip7_aerosol_air_anthro_list(args, config, species, constraint):
    """Load, concatenate, and vertically integrate aircraft anthropogenic
    aerosol emissions.

    Args:
        args (argparse.Namespace): Command-line arguments.
        config (dataset.DatasetConfig): Configuration of the emissions
            dataset, with one or more time ranges.
        species (str): Aerosol species name.
        constraint (iris.Constraint or None): Loading constraint.

    Returns:
        iris.cube.Cube: Concatenated and altitude-collapsed Iris cube.
    """
    datasets = config.to_dataset_sequence(
        variable_id=anthro_variable(species, aircraft=True)
    )
    cube = load_cmip7_aerosol_list(datasets, constraint)
    fix_coords(args, cube)
    if cube.coords("altitude"):
        cube = cube.collapsed(["altitude"], iris.analysis.SUM)
        cube.remove_coord("altitude")
    return cube


def load_cmip7_aerosol_anthro_list(args, config, species, constraint):
    """Load, concatenate, and harmonize surface anthropogenic aerosol emissions
    across multiple files.

    Args:
        args (argparse.Namespace): Command-line arguments.
        config (dataset.DatasetConfig): Configuration of the surface
            emissions dataset, with one or more time ranges.
        species (str): Aerosol species name.
        constraint (iris.Constraint or None): Loading constraint.

    Returns:
        iris.cube.Cube: Concatenated and coordinate-harmonized Iris cube.
    """
    datasets = config.to_dataset_sequence(variable_id=anthro_variable(species))
    cube = load_cmip7_aerosol_list(datasets, constraint)
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
        load_fn (callable): Function returning an Iris cube given species.
        species (str): Aerosol species name.
        stash_item (int): UM STASH item number.
        save_dirpath (pathlib.Path): Destination directory for the ancillary
            file.
    """
    cube = load_fn(species)
    cube_tot = cube.collapsed(["sector"], iris.analysis.SUM)
    esm_cube = cube_tot.regrid(esm_grid_mask_cube(args), INTERPOLATION_SCHEME)
    esm_cube.data = esm_cube.data.filled(0.0)
    zero_poles(esm_cube)
    esm_cube.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=stash_item
    )
    save_ancil(esm_cube, save_dirpath, args.save_filename)
