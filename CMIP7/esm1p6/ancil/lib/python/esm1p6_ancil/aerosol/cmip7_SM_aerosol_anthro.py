from argparse import ArgumentParser
from pathlib import Path

import iris
from aerosol.cmip7_aerosol_anthro import cmip7_aerosol_anthro_interpolate
from aerosol.cmip7_aerosol_common import load_cmip7_aerosol
from aerosol.cmip7_SM_aerosol import esm_sm_aerosol_save_dirpath
from cmip7_ancil_argparse import common_parser, ext_parser
from cmip7_ancil_common import (
    cmip7_date_constraint_from_years,
    extend_years,
    fix_coords,
    interpolate_monthly,
)
from cmip7_SM import CMIP7_SM_BEG_YEAR, CMIP7_SM_END_YEAR, CMIP7_SM_EXT_END_YEAR
from iris.util import equalise_attributes, unify_time_units


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
        parents=[common_parser(), ext_parser()],
    )
    parser.add_argument("--scenario")
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def _anthro_dirpath(source_dirname, dataset_version, dataset_vdate, variable):
    """Construct the source directory path for ScenarioMIP anthropogenic
    aerosol datasets.

    Args:
        source_dirname (str or pathlib.Path): Root input directory.
        dataset_version (str): Dataset version string.
        dataset_vdate (str): Dataset release date string.
        variable (str): Emission variable name.

    Returns:
        pathlib.Path: Resolved directory path.
    """
    return (
        Path(source_dirname)
        / "ScenarioMIP"
        / "IIASA-IAMC"
        / dataset_version
        / "atmos"
        / "mon"
        / variable
        / "gn"
        / dataset_vdate
    )


def cmip7_sm_aerosol_air_anthro_filepath(args, species, date_range):
    """Construct the file path for ScenarioMIP aircraft anthropogenic
    emissions.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        date_range (str): Date range string.

    Returns:
        pathlib.Path: Path to aircraft netCDF file.
    """
    dirpath = _anthro_dirpath(
        args.cmip7_source_data_dirname,
        args.dataset_air_version,
        args.dataset_air_vdate,
        f"{species}_em_AIR_anthro",
    )
    filename = (
        f"{species}-em-AIR-anthro_input4MIPs_emissions_ScenarioMIP_"
        f"{args.dataset_air_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def cmip7_sm_aerosol_anthro_filepath(args, species, date_range):
    """Construct the file path for ScenarioMIP surface anthropogenic emissions.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        date_range (str): Date range string.

    Returns:
        pathlib.Path: Path to surface netCDF file.
    """
    dirpath = _anthro_dirpath(
        args.cmip7_source_data_dirname,
        args.dataset_version,
        args.dataset_vdate,
        f"{species}_em_anthro",
    )
    filename = (
        f"{species}-em-anthro_input4MIPs_emissions_ScenarioMIP_"
        f"{args.dataset_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def cmip7_sm_aerosol_ext_anthro_filepath(
    args, species, date_range, ext_version, ext_vdate
):
    """Construct the file path for ScenarioMIP surface extension emissions
    beyond 2100.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        date_range (str): Extension date range string.
        ext_version (str): Extension dataset version.
        ext_vdate (str): Extension dataset release date.

    Returns:
        pathlib.Path: Path to extension surface netCDF file.
    """
    dirpath = _anthro_dirpath(
        args.cmip7_source_data_dirname,
        ext_version,
        ext_vdate,
        f"{species}_em_anthro",
    )
    filename = (
        f"{species}-em-anthro_input4MIPs_emissions_ScenarioMIP_"
        f"{ext_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def cmip7_sm_aerosol_air_ext_anthro_filepath(
    args, species, date_range, ext_version, ext_vdate
):
    """Construct the file path for ScenarioMIP aircraft extension emissions
    beyond 2100.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        date_range (str): Extension date range string.
        ext_version (str): Extension dataset version.
        ext_vdate (str): Extension dataset release date.

    Returns:
        pathlib.Path: Path to extension aircraft netCDF file.
    """
    dirpath = _anthro_dirpath(
        args.cmip7_source_data_dirname,
        ext_version,
        ext_vdate,
        f"{species}_em_AIR_anthro",
    )
    filename = (
        f"{species}-em-AIR-anthro_input4MIPs_emissions_ScenarioMIP_"
        f"{ext_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def load_cmip7_sm_aerosol_air_anthro(args, species):
    """Load, vertically collapse, interpolate monthly, and extend ScenarioMIP
    aircraft emissions.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.

    Returns:
        iris.cube.Cube: Processed monthly aircraft emissions cube.
    """
    target_end_year = CMIP7_SM_END_YEAR
    ext_cube = None

    if args.ext:
        ext_version = args.dataset_air_ext_version
        ext_vdate = args.dataset_air_ext_vdate
        ext_date_range = args.dataset_air_ext_date_range
        target_end_year = args.end_year or CMIP7_SM_EXT_END_YEAR
        ext_path = cmip7_sm_aerosol_air_ext_anthro_filepath(
            args, species, ext_date_range, ext_version, ext_vdate
        )
        ext_cube = iris.load_cube(
            ext_path,
            cmip7_date_constraint_from_years(
                CMIP7_SM_END_YEAR + 1, target_end_year
            ),
        )

    base_cube = load_cmip7_aerosol(
        args,
        cmip7_sm_aerosol_air_anthro_filepath,
        species,
        args.dataset_date_range,
        cmip7_date_constraint_from_years(CMIP7_SM_BEG_YEAR, CMIP7_SM_END_YEAR),
    )

    if ext_cube is not None:
        cubelist = iris.cube.CubeList([base_cube, ext_cube])
        equalise_attributes(cubelist)
        unify_time_units(cubelist)
        cube = cubelist.concatenate_cube()
    else:
        cube = base_cube

    fix_coords(args, cube)
    if cube.coords("altitude"):
        cube = cube.collapsed(["altitude"], iris.analysis.SUM)
        cube.remove_coord("altitude")
    interpolated = interpolate_monthly(cube, CMIP7_SM_BEG_YEAR, target_end_year)
    return extend_years(interpolated)


def load_cmip7_sm_aerosol_anthro(args, species, collapse_sector=False):
    """Load, optionally collapse sectors, interpolate monthly, and extend
    ScenarioMIP surface emissions.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        collapse_sector (bool, optional): Whether to sum over sector
            coordinate. Defaults to False.

    Returns:
        iris.cube.Cube: Processed monthly surface emissions cube.
    """
    target_end_year = CMIP7_SM_END_YEAR
    ext_cube = None

    if args.ext:
        ext_version = args.dataset_ext_version
        ext_vdate = args.dataset_ext_vdate
        ext_date_range = args.dataset_ext_date_range
        target_end_year = args.end_year or CMIP7_SM_EXT_END_YEAR
        ext_path = cmip7_sm_aerosol_ext_anthro_filepath(
            args, species, ext_date_range, ext_version, ext_vdate
        )
        ext_cube = iris.load_cube(
            ext_path,
            cmip7_date_constraint_from_years(
                CMIP7_SM_END_YEAR + 1, target_end_year
            ),
        )

    base_cube = load_cmip7_aerosol(
        args,
        cmip7_sm_aerosol_anthro_filepath,
        species,
        args.dataset_date_range,
        cmip7_date_constraint_from_years(CMIP7_SM_BEG_YEAR, CMIP7_SM_END_YEAR),
    )

    if ext_cube is not None:
        cubelist = iris.cube.CubeList([base_cube, ext_cube])
        equalise_attributes(cubelist)
        unify_time_units(cubelist)
        cube = cubelist.concatenate_cube()
    else:
        cube = base_cube

    fix_coords(args, cube)
    if collapse_sector and cube.coords("sector"):
        cube = cube.collapsed(["sector"], iris.analysis.SUM)
        cube.remove_coord("sector")
    interpolated = interpolate_monthly(cube, CMIP7_SM_BEG_YEAR, target_end_year)
    return extend_years(interpolated)


def cmip7_sm_aerosol_anthro_interpolate(args, species, stash_item):
    """Interpolate ScenarioMIP anthropogenic aerosol emissions and save to
    ancillary file.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Aerosol species name.
        stash_item (int): UM STASH item number.
    """
    cmip7_aerosol_anthro_interpolate(
        args,
        load_cmip7_sm_aerosol_anthro,
        species,
        stash_item,
        esm_sm_aerosol_save_dirpath(args),
    )
