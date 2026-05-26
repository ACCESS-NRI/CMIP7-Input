from pathlib import Path

import cftime
import iris
import numpy as np
from cmip7_ancil_constants import MONTHS_IN_A_YEAR

NBR_OF_BANDS = 4
NBR_TAPER_YEARS = 10
SAOD_ARRAY_END_YEAR = 2300
# The prescribed wavelength for stratospheric aerosol optical depth
SAOD_WAVELENGTH = 550.0 * 1e-9


def cmip7_volcanic_dirpath(args, activity, period):
    return (
        Path(args.cmip7_source_data_dirname)
        / activity
        / "uoexeter"
        / args.dataset_version
        / "atmos"
        / period
        / "ext"
        / "gnz"
        / args.dataset_vdate
    )


def constrain_to_wavelength(cube, wavelength):
    """
    Constrain to just the prescribed wavelength.
    """
    wl_constraint = iris.Constraint(radiation_wavelength=wavelength)
    return cube.extract(wl_constraint)


def mean_over_latitudes(cube):
    """
    Find the mean over all latitude bands, weighted by area.
    """
    lat_weights = iris.analysis.cartography.cosine_latitude_weights(cube)
    return cube.collapsed(["latitude"], iris.analysis.MEAN, weights=lat_weights)


def sum_over_height_layers(cube):
    """
    Calculate the stratospheric aerosol optical depth by
    summing over stratospheric layers, weighted by layer height.
    """
    height_coord = next(
        c
        for c in cube.coords()
        if c.standard_name == "height_above_mean_sea_level"
    )
    height_weights = np.diff(height_coord.bounds).flatten()
    return cube.collapsed(
        ["height_above_mean_sea_level"],
        iris.analysis.SUM,
        weights=height_weights,
    )


def constrain_to_year_month(cube, year, month):
    """
    Constrain to a given year and month. See #iris.coords.Cell.point in
    scitools-iris.readthedocs.io/en/stable/generated/api/iris.coords.html
    """
    calendar = "proleptic_gregorian"
    beg_date = cftime.datetime(year, month, 1, calendar=calendar)
    end_year = year + 1 if month == MONTHS_IN_A_YEAR else year
    end_month = 1 if month == MONTHS_IN_A_YEAR else month + 1
    end_date = cftime.datetime(end_year, end_month, 1, calendar=calendar)
    ym_constraint = iris.Constraint(
        time=lambda cell: beg_date <= cell.point < end_date
    )
    return cube.extract(ym_constraint)


def constrain_to_latitude_band(cube, band):
    """
    Constrain to one of four equal latitude bands.
    """
    lat_bound = [90, 30, 0, -30, -90]
    lat_constraint = iris.Constraint(
        latitude=(
            lambda cell: lat_bound[band] > cell.point >= lat_bound[band + 1]
        )
    )
    return cube.extract(lat_constraint)


def taper_saod(
    volcanic_end_year,
    saod_for_beg_year,
    saod_for_end_year,
):
    """
    Interpolate between the saod values in saod_for_beg_year
    and saod_for_end_year. The SAOD values taper from saod_for_end_year
    towards saod_for_beg_year for NBR_TAPER_YEARS, and remain at
    saod_for_beg_year afterwards.
    """
    RATIO_ARRAY_LEN = SAOD_ARRAY_END_YEAR - volcanic_end_year
    saod_array = np.zeros((RATIO_ARRAY_LEN, MONTHS_IN_A_YEAR, NBR_OF_BANDS))
    ratio_array = np.zeros(RATIO_ARRAY_LEN)
    for index in range(RATIO_ARRAY_LEN):
        ratio_array[index] = (index + 1) / float(NBR_TAPER_YEARS)
    ratio_endpoints = np.array([0.0, 1.0])
    for month_m1 in range(MONTHS_IN_A_YEAR):
        # Divide into latitude bands.
        for lat_band_nbr in range(NBR_OF_BANDS):
            saod_beg = saod_for_beg_year[month_m1, lat_band_nbr]
            saod_end = saod_for_end_year[month_m1, lat_band_nbr]
            saod_endpoints = np.array([saod_end, saod_beg])
            saod_array[:, month_m1, lat_band_nbr] = np.interp(
                ratio_array, ratio_endpoints, saod_endpoints
            )
    return saod_array


def save_year_tapered_saod(
    year, tapered_saod_array, volcanic_end_year, save_file
):
    """
    Save one year's worth of interpolated saod values in save_file.
    """
    index = year - (volcanic_end_year + 1)
    for month in range(1, MONTHS_IN_A_YEAR + 1):
        print(f"{year:4d} {month:4d}", end="", file=save_file)

        # Divide into latitude bands.
        for lat_band_nbr in range(NBR_OF_BANDS):
            saod = tapered_saod_array[index, month - 1, lat_band_nbr]
            print(
                f"{saod:7.1f}",
                end="",
                file=save_file,
            )
        print(file=save_file)


def save_stratospheric_aerosol_optical_depth(
    args, volcanic_beg_year, volcanic_end_year, dataset_path, save_dirpath
):
    """
    Calculate the average stratospheric aerosol optical depth (SAOD)
    for each historical month by averaging extinction over latitude,
    and summing over stratospheric layers. Save to the save file.
    """
    # Load the dataset into an Iris cube.
    cube = iris.load_cube(dataset_path)

    # Constrain to just the CMIP7 prescribed wavelength.
    cube = constrain_to_wavelength(cube, SAOD_WAVELENGTH)

    # Replace NaN values with 0.
    np.nan_to_num(cube.data, copy=False)

    # Ensure that the save directory exists.
    save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
    save_filepath = save_dirpath / args.save_filename
    # Keep the BEG_YEAR and END_YEAR SAOD values in arrays.
    saod_for_beg_year = np.zeros((MONTHS_IN_A_YEAR, NBR_OF_BANDS))
    saod_for_end_year = np.zeros((MONTHS_IN_A_YEAR, NBR_OF_BANDS))
    with open(save_filepath, "w") as save_file:
        # Iterate over years and months.
        for year in range(volcanic_beg_year, volcanic_end_year + 1):
            for month in range(1, MONTHS_IN_A_YEAR + 1):
                print(f"{year:4d} {month:4d}", end="", file=save_file)
                ym_cube = constrain_to_year_month(cube, year, month)

                # Divide into latitude bands.
                for lat_band_nbr in range(NBR_OF_BANDS):
                    lat_cube = constrain_to_latitude_band(ym_cube, lat_band_nbr)

                    # Find the mean over all latitudes included in this band,
                    # weighted by area.
                    lat_cube = mean_over_latitudes(lat_cube)

                    # Calculate the stratospheric aerosol optical depth
                    # by summing over stratospheric layers,
                    # weighted by layer height.
                    lat_cube = sum_over_height_layers(lat_cube)
                    saod = lat_cube.data * 10000.0
                    print(
                        f"{saod:7.1f}",
                        end="",
                        file=save_file,
                    )
                    # Save the SAOD values for volcanic_beg_year.
                    if year == volcanic_beg_year:
                        saod_for_beg_year[month - 1, lat_band_nbr] = saod
                    # Save the SAOD values for volcanic_end_year.
                    if year == volcanic_end_year:
                        saod_for_end_year[month - 1, lat_band_nbr] = saod
                print(file=save_file)
        # For years from volcanic_end_year + 1 to SAOD_ARRAY_END_YEAR
        # interpolate between the saod values in saod_for_beg_year and
        # saod_for_end_year and save values in save_file.
        tapered_saod_array = taper_saod(saod_for_beg_year, saod_for_end_year)
        for year in range(volcanic_end_year + 1, SAOD_ARRAY_END_YEAR + 1):
            save_year_tapered_saod(
                year, tapered_saod_array, volcanic_end_year, save_file
            )
