from argparse import ArgumentParser
from functools import partial

import iris
from aerosol.cmip7_aerosol_anthro import (
    anthro_variable,
    cmip7_aerosol_anthro_interpolate,
)
from aerosol.cmip7_SM_aerosol import (
    esm_sm_aerosol_save_dirpath,
    load_cmip7_sm_aerosol_series,
    sm_configs,
    sm_target_end_year,
)
from cmip7_ancil_argparse import (
    config_parser,
    ext_parser,
    grid_parser,
    path_parser,
)
from cmip7_ancil_common import (
    extend_years,
    fix_coords,
    interpolate_monthly,
)
from cmip7_SM import CMIP7_SM_BEG_YEAR


def parse_args(species):
    """Parse command-line arguments for ScenarioMIP aerosol emission
    interpolation.

    Args:
        species (str): Target aerosol species name.

    Returns:
        argparse.Namespace: Parsed CLI arguments.
    """
    parser = ArgumentParser(
        prog=f"cmip7_SM_{species}_interpolate",
        description=(
            f"Generate input files from CMIP7 ScenarioMIP {species} forcings"
        ),
        parents=[path_parser(), grid_parser(), config_parser(), ext_parser()],
    )
    parser.add_argument("--scenario")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def load_cmip7_sm_aerosol_air_anthro(args, config, ext_config, species):
    """Load, vertically collapse, interpolate monthly, and extend ScenarioMIP
    aircraft emissions.

    Args:
        args (argparse.Namespace): Command-line arguments.
        config (dataset.DatasetConfig): Configuration of the aircraft
            emissions dataset.
        ext_config (dataset.DatasetConfig or None): Configuration of the
            aircraft emissions extension dataset, or None.
        species (str): Aerosol species name.

    Returns:
        iris.cube.Cube: Processed monthly aircraft emissions cube.
    """
    cube = load_cmip7_sm_aerosol_series(
        args, config, ext_config, anthro_variable(species, aircraft=True)
    )
    fix_coords(args, cube)
    if cube.coords("altitude"):
        cube = cube.collapsed(["altitude"], iris.analysis.SUM)
        cube.remove_coord("altitude")
    interpolated = interpolate_monthly(
        cube, CMIP7_SM_BEG_YEAR, sm_target_end_year(args)
    )
    return extend_years(interpolated)


def load_cmip7_sm_aerosol_anthro(
    args, config, ext_config, species, collapse_sector=False
):
    """Load, optionally collapse sectors, interpolate monthly, and extend
    ScenarioMIP surface emissions.

    Args:
        args (argparse.Namespace): Command-line arguments.
        config (dataset.DatasetConfig): Configuration of the surface
            emissions dataset.
        ext_config (dataset.DatasetConfig or None): Configuration of the
            surface emissions extension dataset, or None.
        species (str): Aerosol species name.
        collapse_sector (bool, optional): Whether to sum over sector
            coordinate. Defaults to False.

    Returns:
        iris.cube.Cube: Processed monthly surface emissions cube.
    """
    cube = load_cmip7_sm_aerosol_series(
        args, config, ext_config, anthro_variable(species)
    )
    fix_coords(args, cube)
    if collapse_sector and cube.coords("sector"):
        cube = cube.collapsed(["sector"], iris.analysis.SUM)
        cube.remove_coord("sector")
    interpolated = interpolate_monthly(
        cube, CMIP7_SM_BEG_YEAR, sm_target_end_year(args)
    )
    return extend_years(interpolated)


def cmip7_sm_aerosol_anthro_interpolate(args, species, stash_item):
    """Interpolate ScenarioMIP anthropogenic aerosol emissions and save to
    ancillary file.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        stash_item (int): UM STASH item number.
    """
    config, ext_config = sm_configs(args)
    cmip7_aerosol_anthro_interpolate(
        args,
        partial(load_cmip7_sm_aerosol_anthro, args, config, ext_config),
        species,
        stash_item,
        esm_sm_aerosol_save_dirpath(args),
    )
