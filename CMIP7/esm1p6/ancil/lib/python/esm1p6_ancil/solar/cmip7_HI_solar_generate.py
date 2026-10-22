from argparse import ArgumentParser

from cmip7_ancil_argparse import (
    config_parser,
    grid_parser,
    pad_parser,
    path_parser,
)
from cmip7_HI import (
    CMIP7_HI_BEG_YEAR,
    CMIP7_HI_END_YEAR,
    esm_hi_forcing_save_dirpath,
)
from dataset import DatasetConfig
from solar.cmip7_solar import (
    cmip7_solar_save,
    load_cmip7_solar_cube,
)


def parse_args():
    """Parse command-line arguments for historical solar forcing generation.

    Returns:
        argparse.Namespace: Parsed CLI arguments containing path, config,
            pad, and save filename parameters.
    """
    parser = ArgumentParser(
        prog="cmip7_HI_solar_generate",
        description=(
            "Generate input files from CMIP7 historical solar forcings"
        ),
        parents=[
            path_parser(),
            grid_parser(),
            config_parser(),
            pad_parser(),
        ],
    )
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_hi_solar_save(args, cube):
    """Save the TSI values for each year into a text file.

    Args:
        args (argparse.Namespace): Command-line arguments specifying pad and
            output options.
        cube (iris.cube.Cube): Loaded historical solar irradiance cube.
    """
    save_dirpath = esm_hi_forcing_save_dirpath(args)
    if args.pad:
        cmip7_solar_save(
            args, cube, CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR, save_dirpath
        )
    else:
        cmip7_solar_save(
            args,
            cube,
            CMIP7_HI_BEG_YEAR,
            CMIP7_HI_END_YEAR,
            save_dirpath,
            save_beg_year=CMIP7_HI_BEG_YEAR,
            save_end_year=CMIP7_HI_END_YEAR,
        )


if __name__ == "__main__":
    args = parse_args()

    config = DatasetConfig.from_yaml(args.config)
    solar_irradiance_cube = load_cmip7_solar_cube(config.to_dataset())

    cmip7_hi_solar_save(args, solar_irradiance_cube)
