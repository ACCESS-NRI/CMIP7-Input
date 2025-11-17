from argparse import ArgumentParser

import iris
from esm1p6_ancil.cmip7_ancil_argparse import common_parser
from esm1p6_ancil.cmip7_HI import (
    CMIP7_HI_BEG_YEAR,
    CMIP7_HI_END_YEAR,
    esm_hi_forcing_save_dirpath,
)
from esm1p6_ancil.solar.cmip7_solar import cmip7_solar_dirpath, load_cmip7_solar_cube


def parse_args():
    parser = ArgumentParser(
        prog="cmip7_HI_solar_generate",
        description=(
            "Generate input files from CMIP7 historical solar forcings"
        ),
        parents=[
            common_parser(),
        ],
    )
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_hi_solar_save(args, cube):
    save_dirpath = esm_hi_forcing_save_dirpath(args)
    # Ensure that the save directory exists.
    save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
    save_filepath = save_dirpath / args.save_filename
    with open(save_filepath, "w") as save_file:
        for year in range(CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR + 1):
            year_cons = iris.Constraint(
                time=lambda cell: cell.point.year == year
            )
            year_cube = cube.extract(year_cons)
            year_mean = year_cube.collapsed("time", iris.analysis.MEAN).data
            print(year, f"{year_mean:.3f}", file=save_file)


if __name__ == "__main__":
    args = parse_args()

    cmip7_filename = (
        "multiple_input4MIPs_solar_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}.nc"
    )
    cmip7_filepath = cmip7_solar_dirpath(args, "mon") / cmip7_filename

    solar_irradiance_cube = load_cmip7_solar_cube(cmip7_filepath)

    cmip7_hi_solar_save(args, solar_irradiance_cube)
