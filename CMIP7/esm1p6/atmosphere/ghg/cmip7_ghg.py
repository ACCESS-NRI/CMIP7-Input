import cftime
import iris

from pathlib import Path


# Specify the molar mass of each gas in grams per mole
DRY_AIR_MOLAR_MASS = 28.97
GHG_MOLAR_MASS = {
    "co2": 44.01,
    "n2o": 44.01,
    "ch4": 16.04,
    "cfc11": 137.37,
    "cfc12": 120.91,
    "cfc113": 187.375,
    "hcfc22": 86.47,
    "hfc125": 120.02,
    "hfc134a": 102.03}


# Determine the scaling factor used
SCALE_FACTOR = {
    "ppm": 1.0e-6,
    "ppb": 1.0e-9,
    "ppt": 1.0e-12}


def cmip7_pro_greg_date_constraint_from_years(beg_year, end_year):
    """
    For CMIP6 and CMIP7 data.
    The CMIP7 greenhouse gas forcing files use Proleptic Gregorian
    """
    beg_date = cftime.DatetimeProlepticGregorian(beg_year, 1, 1)
    end_date = cftime.DatetimeProlepticGregorian(end_year, 12, 31)
    return iris.Constraint(
            time=lambda cell: beg_date <= cell.point <= end_date)


def cmip7_ghg_dirpath(args, ghg):
    return (
        Path(args.cmip7_source_data_dirname)
        / 'CR'
        / args.dataset_version
        / 'atmos'
        / 'yr'
        / ghg
        / 'gm'
        / args.dataset_vdate)
