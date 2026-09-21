import warnings
from argparse import ArgumentParser
from pathlib import Path

from cmip7_ancil_argparse import common_parser, ext_parser
from cmip7_ancil_common import extend_years, tile_constant_years
from cmip7_ancil_constants import ANCIL_TODAY
from cmip7_SM import CMIP7_SM_END_YEAR, CMIP7_SM_EXT_END_YEAR
from nitrogen.cmip7_nitrogen import (
    cmip7_nitrogen_dirpath,
    load_cmip7_nitrogen,
    regrid_cmip7_nitrogen,
    save_cmip7_nitrogen,
)


def parse_args():
    parser = ArgumentParser(
        parents=[common_parser(), ext_parser()],
        prog="cmip7_SM_nitrogen_generate",
        description=(
            "Generate input files from CMIP7 ScenarioMIP nitrogen forcings"
        ),
    )
    parser.add_argument("--scenario")
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_sm_nitrogen_filepath(args, species):
    dirpath = cmip7_nitrogen_dirpath(args, "ScenarioMIP", "mon", species)
    filename = (
        f"{species}_input4MIPs_surfaceFluxes_ScenarioMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}.nc"
    )
    return dirpath / filename


def esm_sm_nitrogen_save_dirpath(args):
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / f"scen7-{args.scenario}"
        / "atmosphere"
        / "land"
        / "biogeochemistry"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


if __name__ == "__main__":
    args = parse_args()

    # Load the CMIP7 datasets
    try:
        nitrogen_cube = load_cmip7_nitrogen(args, cmip7_sm_nitrogen_filepath)
    except Exception as e:
        warnings.warn(f"Could not load nitrogen dataset: {e}", UserWarning)
        nitrogen_cube = None

    if nitrogen_cube is not None:
        # Regrid to match the ESM1.5 mask and extend the time series
        esm_cube = regrid_cmip7_nitrogen(args, nitrogen_cube)
        if getattr(args, "ext", False):
            target_end_year = (
                getattr(args, "end_year", None) or CMIP7_SM_EXT_END_YEAR
            )
            esm_cube = tile_constant_years(
                esm_cube, CMIP7_SM_END_YEAR, target_end_year
            )
        esm_cube = extend_years(esm_cube)
        # Save the ancillary
        save_cmip7_nitrogen(args, esm_cube, esm_sm_nitrogen_save_dirpath)
