from argparse import ArgumentParser

from cmip7_ancil_argparse import (
    config_parser,
    ext_parser,
    grid_parser,
    pad_parser,
    path_parser,
)
from cmip7_SM import (
    CMIP7_SM_END_YEAR,
    CMIP7_SM_EXT_END_YEAR,
    esm_sm_forcing_save_dirpath,
)
from dataset import DatasetConfig
from solar.cmip7_solar import (
    cmip7_solar_save,
    load_cmip7_solar_cube,
)

CMIP7_SM_SOLAR_BEG_YEAR = 2022
CMIP7_SM_SOLAR_END_YEAR = 2299


def parse_args():
    """Parse command-line arguments for ScenarioMIP solar forcing generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, pad, ext,
            scenario, date range, and save filename parameters.
    """
    parser = ArgumentParser(
        prog="cmip7_SM_solar_generate",
        description=(
            "Generate input files from CMIP7 ScenarioMIP solar forcings"
        ),
        parents=[
            path_parser(),
            grid_parser(),
            config_parser(),
            pad_parser(),
            ext_parser(),
        ],
    )
    parser.add_argument("--scenario")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_sm_solar_save(args, cube):
    """Save the TSI values for each year into a text file.

    Args:
        args (argparse.Namespace): Command-line arguments specifying pad, ext,
            and output options.
        cube (iris.cube.Cube): Loaded ScenarioMIP solar irradiance cube.
    """
    target_end_year = (
        (args.end_year or CMIP7_SM_EXT_END_YEAR)
        if args.ext
        else CMIP7_SM_END_YEAR
    )

    save_dirpath = esm_sm_forcing_save_dirpath(args)
    if args.pad:
        cmip7_solar_save(
            args,
            cube,
            CMIP7_SM_SOLAR_BEG_YEAR,
            target_end_year,
            save_dirpath,
            save_end_year=target_end_year,
        )
    else:
        cmip7_solar_save(
            args,
            cube,
            CMIP7_SM_SOLAR_BEG_YEAR,
            target_end_year,
            save_dirpath,
            save_beg_year=CMIP7_SM_SOLAR_BEG_YEAR,
            save_end_year=target_end_year,
        )


if __name__ == "__main__":
    args = parse_args()

    config = DatasetConfig.from_yaml(args.config)
    solar_irradiance_cube = load_cmip7_solar_cube(config.to_dataset())
    cmip7_sm_solar_save(args, solar_irradiance_cube)
