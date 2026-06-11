from argparse import ArgumentParser
from pathlib import Path

from aerosol.cmip7_aerosol_anthro import cmip7_aerosol_anthro_interpolate
from aerosol.cmip7_aerosol_common import load_cmip7_aerosol_list
from aerosol.cmip7_SM_aerosol import (
    CMIP7_SM_AEROSOL_BEG_YEAR,
    CMIP7_SM_AEROSOL_END_YEAR,
    esm_sm_aerosol_save_dirpath,
)
from cmip7_ancil_argparse import common_parser
from cmip7_ancil_common import (
    cmip7_date_constraint_from_years,
    fix_coords,
)


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


def _anthro_dirpath(args, variable):
    return (
        Path(args.cmip7_source_data_dirname)
        / "ScenarioMIP"
        / "IIASA-IAMC"
        / args.dataset_version
        / "atmos"
        / "mon"
        / variable
        / "gn"
        / args.dataset_vdate
    )


def cmip7_sm_aerosol_air_anthro_filepath(args, species, date_range):
    dirpath = _anthro_dirpath(args, f"{species}_em_AIR_anthro")
    filename = (
        f"{species}-em-AIR-anthro_input4MIPs_emissions_ScenarioMIP_"
        f"{args.dataset_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def cmip7_sm_aerosol_anthro_filepath(args, species, date_range):
    dirpath = _anthro_dirpath(args, f"{species}_em_anthro")
    filename = (
        f"{species}-em-anthro_input4MIPs_emissions_ScenarioMIP_"
        f"{args.dataset_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def load_cmip7_sm_aerosol_air_anthro(
    args,
    species,
    beg_year=CMIP7_SM_AEROSOL_BEG_YEAR,
    end_year=CMIP7_SM_AEROSOL_END_YEAR,
):
    cube = load_cmip7_aerosol_list(
        args,
        cmip7_sm_aerosol_air_anthro_filepath,
        species,
        args.dataset_date_range_list,
        cmip7_date_constraint_from_years(beg_year, end_year),
    )
    fix_coords(args, cube)
    return cube


def load_cmip7_sm_aerosol_anthro(
    args,
    species,
    beg_year=CMIP7_SM_AEROSOL_BEG_YEAR,
    end_year=CMIP7_SM_AEROSOL_END_YEAR,
):
    cube = load_cmip7_aerosol_list(
        args,
        cmip7_sm_aerosol_anthro_filepath,
        species,
        args.dataset_date_range_list,
        cmip7_date_constraint_from_years(beg_year, end_year),
    )
    fix_coords(args, cube)
    return cube


def cmip7_sm_aerosol_anthro_interpolate(args, species, stash_item):
    cmip7_aerosol_anthro_interpolate(
        args,
        load_cmip7_sm_aerosol_anthro,
        species,
        stash_item,
        esm_sm_aerosol_save_dirpath(args),
    )
