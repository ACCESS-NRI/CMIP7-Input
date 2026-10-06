from pathlib import Path

import cftime
import iris
import numpy as np
from cmip7_ancil_constants import MONTHS_IN_A_YEAR

NBR_OF_BANDS = 4
NBR_TAPER_YEARS = 10
SAOD_BEG_YEAR = 1850
SAOD_END_YEAR = 2300
# The prescribed wavelength for stratospheric aerosol optical depth
SAOD_WAVELENGTH = 550.0 * 1e-9
# Scaling ratio to use with calculated SAOD
SAOD_SCALING = 10000.0


def cmip7_volcanic_dirpath(
    args,
    activity,
    period,
    dataset_version,
    dataset_vdate,
):
    """Construct the source directory path for CMIP7 volcanic aerosol datasets.

    Args:
        args (argparse.Namespace): Command-line arguments containing
            cmip7_source_data_dirname.
        activity (str): MIP activity name ('CMIP' or 'ScenarioMIP').
        period (str): Temporal frequency ('mon' or 'monC').
        dataset_version (str): Version string for the volcanic dataset.
        dataset_vdate (str): Dataset version date string.

    Returns:
        pathlib.Path: Directory path under
            uoexeter/{dataset_version}/atmos/{period}/ext/gnz/{dataset_vdate}.
    """
    return (
        Path(args.cmip7_source_data_dirname)
        / activity
        / "uoexeter"
        / dataset_version
        / "atmos"
        / period
        / "ext"
        / "gnz"
        / dataset_vdate
    )


def constrain_to_wavelength(cube, wavelength):
    """Constrain to just the prescribed wavelength.

    Args:
        cube (iris.cube.Cube): Volcanic extinction cube containing
            radiation_wavelength coordinate.
        wavelength (float): Target radiation wavelength in meters (typically
            550 nm = 5.5e-7 m).

    Returns:
        iris.cube.Cube: Extracted cube constrained to the given wavelength.
    """
    wl_constraint = iris.Constraint(radiation_wavelength=wavelength)
    return cube.extract(wl_constraint)


def mean_over_latitudes(cube):
    """Find the mean over all latitude bands, weighted by area.

    Args:
        cube (iris.cube.Cube): Input cube with latitude coordinate.

    Returns:
        iris.cube.Cube: Collapsed cube averaged over latitude using cosine
            weighting.
    """
    lat_weights = iris.analysis.cartography.cosine_latitude_weights(cube)
    return cube.collapsed(["latitude"], iris.analysis.MEAN, weights=lat_weights)


def sum_over_height_layers(cube):
    """Calculate the stratospheric aerosol optical depth by
    summing over stratospheric layers, weighted by layer height.

    Args:
        cube (iris.cube.Cube): Extinction cube with height_above_mean_sea_level
            coordinate and bounds.

    Returns:
        iris.cube.Cube: Collapsed cube with vertical integral of extinction
            (optical depth).
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
    """Constrain to a given year and month. See #iris.coords.Cell.point in
    scitools-iris.readthedocs.io/en/stable/generated/api/iris.coords.html

    Args:
        cube (iris.cube.Cube): Volcanic cube with proleptic Gregorian time
            coordinate.
        year (int): Calendar year.
        month (int): Calendar month (1-12).

    Returns:
        iris.cube.Cube: Extracted single-month cube.
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
    """Constrain to one of four equal latitude bands.

    Args:
        cube (iris.cube.Cube): Input cube with latitude coordinate.
        band (int): Latitude band index (0: 90N-30N, 1: 30N-0, 2: 0-30S, 3:
            30S-90S).

    Returns:
        iris.cube.Cube: Extracted cube restricted to the specified latitude
            range.
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
    save_end_year,
    saod_for_beg_year,
    saod_for_end_year,
):
    """Interpolate between the saod values in saod_for_beg_year
    and saod_for_end_year. The SAOD values taper from saod_for_end_year
    towards saod_for_beg_year for NBR_TAPER_YEARS, and remain at
    saod_for_beg_year afterwards.

    Args:
        volcanic_end_year (int): Last year of available volcanic forcing data.
        save_end_year (int): Target end year for output forcing file.
        saod_for_beg_year (numpy.ndarray): 2D array (12 months x 4 bands) of
            baseline SAOD.
        saod_for_end_year (numpy.ndarray): 2D array (12 months x 4 bands) of
            final-year SAOD.

    Returns:
        numpy.ndarray: 3D array of shaped (n_years, 12, 4) with tapered SAOD
            values.
    """
    RATIO_ARRAY_LEN = save_end_year - volcanic_end_year
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


def _save_year_saod(save_file, year, saod_year):
    """Save 12 monthly SAOD records for a given year to save_file.

    Args:
        save_file (io.TextIOWrapper): Open output text file stream.
        year (int): Calendar year being written.
        saod_year (numpy.ndarray): 2D array of shape (12, 4) with monthly SAOD
            across latitude bands.
    """
    for month in range(1, MONTHS_IN_A_YEAR + 1):
        print(f"{year:4d} {month:4d}", end="", file=save_file)
        for lat_band_nbr in range(NBR_OF_BANDS):
            saod = saod_year[month - 1, lat_band_nbr]
            print(f"{saod:7.1f}", end="", file=save_file)
        print(file=save_file)


def save_early_saod(volcanic_beg_year, save_file, pi_mean_saod):
    """Save the PI average SAOD for all years before volcanic_beg_year.

    Args:
        volcanic_beg_year (int): First year of active volcanic data.
        save_file (io.TextIOWrapper): Open output text file stream.
        pi_mean_saod (float): Pre-industrial mean SAOD constant value.
    """
    early_saod = np.full((MONTHS_IN_A_YEAR, NBR_OF_BANDS), pi_mean_saod)
    for year in range(SAOD_BEG_YEAR, volcanic_beg_year):
        _save_year_saod(save_file, year, early_saod)


def _save_constant_saod(save_file, saod_for_end_year, start_year, end_year):
    """Tile the 12 monthly SAOD values of volcanic_end_year to end_year.

    Args:
        save_file (io.TextIOWrapper): Open output text file stream.
        saod_for_end_year (numpy.ndarray): 2D array (12 months x 4 bands) of
            baseline SAOD.
        start_year (int): First extended year to write.
        end_year (int): Last extended year to write.
    """
    for year in range(start_year, end_year + 1):
        _save_year_saod(save_file, year, saod_for_end_year)


def _save_tapered_saod(
    save_file, volcanic_end_year, save_end_year, saod_for_beg, saod_for_end
):
    """Interpolate between saod_for_beg and saod_for_end and save to file.

    Args:
        save_file (io.TextIOWrapper): Open output text file stream.
        volcanic_end_year (int): End year of active forcing series.
        save_end_year (int): Final year of extended output series.
        saod_for_beg (numpy.ndarray): Baseline SAOD array.
        saod_for_end (numpy.ndarray): End-year SAOD array.
    """
    tapered_saod_array = taper_saod(
        volcanic_end_year,
        save_end_year,
        saod_for_beg,
        saod_for_end,
    )
    for year in range(volcanic_end_year + 1, save_end_year + 1):
        index = year - (volcanic_end_year + 1)
        _save_year_saod(save_file, year, tapered_saod_array[index])


def save_stratospheric_aerosol_optical_depth(
    args,
    volcanic_beg_year,
    volcanic_end_year,
    dataset_path,
    save_dirpath,
    pi_mean_saod=None,
    save_beg_year=SAOD_BEG_YEAR,
    save_end_year=SAOD_END_YEAR,
    hold_constant=False,
):
    """Calculate the average stratospheric aerosol optical depth (SAOD)
    for each month by averaging extinction over latitude,
    and summing over stratospheric layers. Save to the save file.

    Args:
        args (argparse.Namespace): Command-line arguments containing
            save_filename.
        volcanic_beg_year (int): Start year of dataset.
        volcanic_end_year (int): End year of dataset.
        dataset_path (pathlib.Path): Path to raw netCDF input file.
        save_dirpath (pathlib.Path): Destination directory path.
        pi_mean_saod (float, optional): Pre-industrial mean SAOD for padding
            early years. Defaults to None.
        save_beg_year (int, optional): Earliest output year. Defaults to 1850.
        save_end_year (int, optional): Latest output year. Defaults to 2300.
        hold_constant (bool, optional): If True, hold values constant beyond
            volcanic_end_year; if False, taper towards baseline. Defaults to
            False.
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
        # Save the PI average SAOD for all years before volcanic_beg_year.
        if volcanic_beg_year > save_beg_year and pi_mean_saod is not None:
            save_early_saod(volcanic_beg_year, save_file, pi_mean_saod)

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
                    saod = lat_cube.data * SAOD_SCALING
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
        if save_end_year > volcanic_end_year:
            if hold_constant:
                _save_constant_saod(
                    save_file,
                    saod_for_end_year,
                    volcanic_end_year + 1,
                    save_end_year,
                )
            else:
                _save_tapered_saod(
                    save_file,
                    volcanic_end_year,
                    save_end_year,
                    saod_for_beg_year,
                    saod_for_end_year,
                )
