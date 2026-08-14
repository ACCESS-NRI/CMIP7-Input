from argparse import ArgumentParser
from pathlib import Path

import iris
from aerosol.cmip7_aerosol_anthro import cmip7_aerosol_anthro_interpolate
from aerosol.cmip7_aerosol_common import load_cmip7_aerosol
from aerosol.cmip7_SM_aerosol import esm_sm_aerosol_save_dirpath
from cmip7_ancil_argparse import common_parser
from cmip7_ancil_common import (
    cmip7_date_constraint_from_years,
    extend_years,
    fix_coords,
    interpolate_monthly,
)
from cmip7_SM import CMIP7_SM_BEG_YEAR, CMIP7_SM_END_YEAR


def parse_args(species):
    parser = ArgumentParser(
        prog=f"cmip7_SM_{species}_interpolate",
        description=(
            f"Generate input files from CMIP7 ScenarioMIP {species} forcings"
        ),
        parents=[common_parser()],
    )
    parser.add_argument("--scenario")
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def _anthro_dirpath(source_dirname, dataset_version, dataset_vdate, variable):
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
    dirpath = _anthro_dirpath(
        args.cmip7_source_data_dirname,
        args.dataset_air_version,
        args.dataset_air_vdate,
        f"{species}_em_AIR_anthro"
    )
    filename = (
        f"{species}-em-AIR-anthro_input4MIPs_emissions_ScenarioMIP_"
        f"{args.dataset_air_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def cmip7_sm_aerosol_anthro_filepath(args, species, date_range):
    dirpath = _anthro_dirpath(
        args.cmip7_source_data_dirname,
        args.dataset_version,
        args.dataset_vdate,
        f"{species}_em_anthro"
    )
    dirpath = _anthro_dirpath(args, f"{species}_em_anthro")
    filename = (
        f"{species}-em-anthro_input4MIPs_emissions_ScenarioMIP_"
        f"{args.dataset_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def load_cmip7_sm_aerosol_air_anthro(args, species):
    cube = load_cmip7_aerosol(
        args,
        cmip7_sm_aerosol_air_anthro_filepath,
        species,
        args.dataset_date_range,
        cmip7_date_constraint_from_years(CMIP7_SM_BEG_YEAR, CMIP7_SM_END_YEAR),
    )
    fix_coords(args, cube)
    if cube.coords("altitude"):
        cube = cube.collapsed(["altitude"], iris.analysis.SUM)
        cube.remove_coord("altitude")
    interpolated = interpolate_monthly(
        cube, CMIP7_SM_BEG_YEAR, CMIP7_SM_END_YEAR
    )
    return extend_years(interpolated)


def load_cmip7_sm_aerosol_anthro(args, species, collapse_sector=False):
    cube = load_cmip7_aerosol(
        args,
        cmip7_sm_aerosol_anthro_filepath,
        species,
        args.dataset_date_range,
        cmip7_date_constraint_from_years(CMIP7_SM_BEG_YEAR, CMIP7_SM_END_YEAR),
    )
    fix_coords(args, cube)
    if collapse_sector and cube.coords("sector"):
        cube = cube.collapsed(["sector"], iris.analysis.SUM)
        cube.remove_coord("sector")
    interpolated = interpolate_monthly(
        cube, CMIP7_SM_BEG_YEAR, CMIP7_SM_END_YEAR
    )
    return extend_years(interpolated)


def cmip7_sm_aerosol_anthro_interpolate(args, species, stash_item):
    cmip7_aerosol_anthro_interpolate(
        args,
        load_cmip7_sm_aerosol_anthro,
        species,
        stash_item,
        esm_sm_aerosol_save_dirpath(args),
    )
