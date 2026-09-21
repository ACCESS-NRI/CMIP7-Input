import warnings
from argparse import ArgumentParser

from cmip7_ancil_argparse import (
    common_parser,
    ext_parser,
    pad_parser,
)
from cmip7_SM import (
    CMIP7_SM_END_YEAR,
    CMIP7_SM_EXT_END_YEAR,
    esm_sm_forcing_save_dirpath,
)
from solar.cmip7_solar import (
    cmip7_solar_dirpath,
    cmip7_solar_save,
    load_cmip7_solar_cube,
)

CMIP7_SM_SOLAR_BEG_YEAR = 2022
CMIP7_SM_SOLAR_END_YEAR = 2299


def parse_args():
    parser = ArgumentParser(
        prog="cmip7_SM_solar_generate",
        description=(
            "Generate input files from CMIP7 ScenarioMIP solar forcings"
        ),
        parents=[
            common_parser(),
            pad_parser(),
            ext_parser(),
        ],
    )
    parser.add_argument("--scenario")
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_sm_solar_save(args, cube):
    """
    Save the TSI values for each year into a text file.
    """
    is_ext = getattr(args, "ext", False)
    target_end_year = (
        (getattr(args, "end_year", None) or CMIP7_SM_EXT_END_YEAR)
        if is_ext
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

    dirpath = cmip7_solar_dirpath(args, "ScenarioMIP", "mon")
    filename = (
        "multiple_input4MIPs_solar_ScenarioMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}.nc"
    )
    dataset_path = dirpath / filename

    if not dataset_path.exists():
        warnings.warn(
            f"ScenarioMIP solar dataset {dataset_path} not found.",
            UserWarning,
        )
    else:
        solar_irradiance_cube = load_cmip7_solar_cube(dataset_path)
        cmip7_sm_solar_save(args, solar_irradiance_cube)
