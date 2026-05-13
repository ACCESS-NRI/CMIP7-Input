import argparse
from pathlib import Path

import cf_units
import cftime
import iris
import numpy as np
from cmip7_ancil_argparse import common_parser
from cmip7_ancil_common import (
    esm_grid_mask_cube,
    save_ancil,
)
from cmip7_ancil_constants import ANCIL_TODAY
from co2.cmip7_EH_CO2_interpolate import STASH_ITEM

# Length of the declining emissions section
INTERPOLATION_NYEARS = 100
# Length of the constant -10PgC/year section
FLAT_MINUS10_NYEARS = 100

# CO2 flux (kg CO2 /m2/s) corresponding to emissions of 10PgC/year.
# Taken from the flat10 ancillary:
# /g/data/vk83/prerelease/configurations/inputs/access-esm1p6/modern/flat10/
# atmosphere/forcing/global.N96/2025.12.05/CO2_fluxes_flat10.anc
PG10_C = np.float64(2.2802997268200897451606579124927520751953125e-09)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="cmip7_F10CDR_CO2_generate",
        description=(
            "Generate CO2 emissions for the CMIP7 esm-flat10-cdr experiment"
        ),
        parents=[common_parser()],
    )
    parser.add_argument(
        "--year-start",
        help="Initial year in file.",
        required=True,
        type=int,
    )
    parser.add_argument(
        "--nyear-zero",
        help="Number of years of zero emissions to add to the end.",
        required=True,
        type=int,
    )
    parser.add_argument("--save-filename")

    return parser.parse_args()


def f10cdr_co2_save_dirpath(args):
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "flat10-cdr"
        / "atmosphere"
        / "forcing"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


def create_f10cdr_data(nyear_zero, esm_latitude, esm_longitude):
    """
    Create a numpy array of CO2 emissions following the flat10-cdr
    specification of linearly declining emissions from 10PgC to -10PgC
    over 100 years, followed by flat emissions of 10PgC for 100 years,
    and zero emissions for the remaining duration.
    """
    # Emissions decline each January and remain flat for the rest of each year.
    yearly_vals = np.linspace(
        start=PG10_C, stop=-PG10_C, num=INTERPOLATION_NYEARS + 1
    )
    decline_section = np.zeros(
        shape=(
            INTERPOLATION_NYEARS * 12 + 1,
            esm_latitude.shape[0],
            esm_longitude.shape[0],
        )
    )

    for i in range(decline_section.shape[0]):
        decline_year = i // 12
        decline_section[i, :, :] = np.full(
            shape=(esm_latitude.shape[0], esm_longitude.shape[0]),
            fill_value=yearly_vals[decline_year],
        )

    flat_minus10_section = np.full(
        shape=(
            FLAT_MINUS10_NYEARS * 12 - 1,
            esm_latitude.shape[0],
            esm_longitude.shape[0],
        ),
        fill_value=-PG10_C,
    )

    zero_section = np.full(
        shape=(nyear_zero * 12, esm_latitude.shape[0], esm_longitude.shape[0]),
        fill_value=0.0,
        dtype=np.float64,
    )

    flat10_cdr_data = np.concatenate(
        [decline_section, flat_minus10_section, zero_section], axis=0
    )

    return flat10_cdr_data


def create_f10cdr_times(flat10_cdr_data, year_start):
    """
    Create a time dimension coordinate for the flat10-cdr CO2 emissions cube.
    """
    time_units = cf_units.Unit(f"days since {year_start}-01-01")
    n_months = flat10_cdr_data.shape[0]

    # Arrays to fill
    time_vals = np.zeros(n_months)
    time_bnds = np.zeros((n_months, 2))

    for i in range(n_months):
        year = year_start + i // 12
        month = i % 12 + 1
        date = cftime.DatetimeProlepticGregorian(year, month, 1)
        time_vals[i] = time_units.date2num(date)
        if month == 12:
            next_date = cftime.DatetimeProlepticGregorian(year + 1, 1, 1)
        else:
            next_date = cftime.DatetimeProlepticGregorian(year, month + 1, 1)

        time_bnds[i, 0] = time_vals[i]
        time_bnds[i, 1] = time_units.date2num(next_date)

    time_coord = iris.coords.DimCoord(
        time_vals,
        var_name="time",
        units=time_units,
    )
    time_coord.bounds = time_bnds

    return time_coord


def create_f10cdr_cube(
    flat10_cdr_data, flat10_cdr_times, esm_latitude, esm_longitude
):
    """
    Create an iris cube with data and coordinates for the flat10-cdr
    CO2 emissions.
    """
    flat10_cdr_cube = iris.cube.Cube(flat10_cdr_data)
    flat10_cdr_cube.add_dim_coord(
        flat10_cdr_times,
        0,
    )
    flat10_cdr_cube.add_dim_coord(
        esm_latitude,
        1,
    )
    flat10_cdr_cube.add_dim_coord(
        esm_longitude,
        2,
    )
    flat10_cdr_cube.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=STASH_ITEM
    )

    return flat10_cdr_cube


def cmip7_f10cdr_co2_generate(args):
    esm_longitude = esm_grid_mask_cube(args).coord("longitude")
    esm_latitude = esm_grid_mask_cube(args).coord("latitude")
    f10cdr_data = create_f10cdr_data(
        args.nyear_zero, esm_latitude, esm_longitude
    )
    f10cdr_times = create_f10cdr_times(f10cdr_data, args.year_start)
    f10cdr_cube = create_f10cdr_cube(
        f10cdr_data, f10cdr_times, esm_latitude, esm_longitude
    )
    save_dirpath = f10cdr_co2_save_dirpath(args)
    save_ancil(f10cdr_cube, save_dirpath, args.save_filename)


if __name__ == "__main__":
    args = parse_args()
    cmip7_f10cdr_co2_generate(args)
