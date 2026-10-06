"""Common coordinate transformation, time interpolation, grid alignment, and
ancillary save utilities.
"""

import tempfile
from os import fsdecode
from pathlib import Path

import ants
import ants.io
import ants.io.save as save
import cf_units
import cftime
import iris
import iris.analysis
import iris.coord_categorisation
import iris.util
import mule
import numpy as np
from cmip7_ancil_constants import (
    MONTHS_IN_A_YEAR,
    UM_VERSION,
)
from iris.util import equalise_attributes

iris.FUTURE.datum_support = True

INTERPOLATION_SCHEME = iris.analysis.AreaWeighted(mdtol=0.5)


def cmip7_date_constraint_from_years(beg_year, end_year):
    """Create an Iris temporal constraint for CMIP6 and CMIP7 NoLeap calendar
    datasets.

    Args:
        beg_year (int): Starting calendar year (inclusive).
        end_year (int): Ending calendar year (inclusive).

    Returns:
        iris.Constraint: Time coordinate constraint spanning January 1 of
            ``beg_year`` to December 31 of ``end_year`` on a NoLeap calendar.
    """
    # For CMIP6 and CMIP7 data
    beg_date = cftime.DatetimeNoLeap(beg_year, 1, 1)
    end_date = cftime.DatetimeNoLeap(end_year, 12, 31)
    return iris.Constraint(time=lambda cell: beg_date <= cell.point <= end_date)


def esm_grid_mask_filepath(args):
    """Construct the filesystem path to the ACCESS-ESM1.5 grid land-sea mask
    file.

    Args:
        args (argparse.Namespace): Parsed CLI arguments containing
            ``esm15_inputs_dirname``, ``esm_grid_rel_dirname``, and
            ``esm15_grid_version``.

    Returns:
        pathlib.Path: Full path to ``qrparm.mask``.
    """
    return (
        Path(args.esm15_inputs_dirname)
        / "modern"
        / "share"
        / "atmosphere"
        / "grids"
        / args.esm_grid_rel_dirname
        / args.esm15_grid_version
        / "qrparm.mask"
    )


def esm_grid_mask_cube(args):
    """Load the ACCESS-ESM1.5 target grid mask and construct coordinate bounds.

    Args:
        args (argparse.Namespace): Parsed CLI arguments with grid
            configuration.

    Returns:
        iris.cube.Cube: Land-sea mask cube with guessed latitude and longitude
            bounds.
    """
    cube = iris.load_cube(esm_grid_mask_filepath(args))
    cube.coord("latitude").guess_bounds()
    cube.coord("longitude").guess_bounds()
    return cube


def set_gregorian(var, replace_bounds=False):
    """Convert an Iris cube's time coordinate and bounds to the Proleptic
    Gregorian calendar.

    Args:
        var (iris.cube.Cube): Cube whose time coordinate will be converted in
            place.
        replace_bounds (bool, optional): If True, replaces existing monthly
            bounds with reconstructed first-of-month to first-of-next-month
            intervals. Defaults to False.
    """
    # Change the calendar to Gregorian for the model
    time = var.coord("time")
    origin = time.units.origin
    newunits = cf_units.Unit(origin, calendar="proleptic_gregorian")

    tvals = np.array(time.points)
    tbnds = np.array(time.bounds)
    for i in range(len(time.points)):
        date = time.units.num2date(tvals[i])
        newdate = cftime.DatetimeProlepticGregorian(
            date.year, date.month, date.day, date.hour, date.minute, date.second
        )
        tvals[i] = newunits.date2num(newdate)
        if replace_bounds:
            beg_date = cftime.DatetimeProlepticGregorian(
                date.year,
                date.month,
                1,
                date.hour,
                date.minute,
                date.second,
            )
            tbnds[i][0] = newunits.date2num(beg_date)
            if date.month == 12:
                end_year = date.year + 1
                end_month = 1
            else:
                end_year = date.year
                end_month = date.month + 1
            end_date = cftime.DatetimeProlepticGregorian(
                end_year,
                end_month,
                1,
                date.hour,
                date.minute,
                date.second,
            )
            tbnds[i][1] = newunits.date2num(end_date)
        else:
            for j in range(2):
                date = time.units.num2date(tbnds[i][j])
                newdate = cftime.DatetimeProlepticGregorian(
                    date.year,
                    date.month,
                    date.day,
                    date.hour,
                    date.minute,
                    date.second,
                )
                tbnds[i][j] = newunits.date2num(newdate)
    time.points = tvals
    time.bounds = tbnds
    time.units = newunits


def extend_years(cube):
    """Extend a cube representing a monthly time series by duplicating and
    adjusting the first and last years.

    Based on Crown copyright code from ozone_cmip6_ancillary_for_suite.py
    by Steven Hardiman of the UK Met Office.

    Args:
        cube (iris.cube.Cube): Input Iris cube containing a monthly time
            series. Must contain at least two full years of monthly data.

    Returns:
        iris.cube.Cube: Concatenated cube with prepended preceding year and
            appended following year with shifted time coordinates and bounds.
    """
    time_coord = cube.coord("time")
    time_points = time_coord.points
    # Do not extend a cube containing less than two years of data.
    if len(time_points) < MONTHS_IN_A_YEAR * 2:
        return cube

    # Duplicate the first year.
    length_one_year = time_points[MONTHS_IN_A_YEAR] - time_points[0]
    beg_year = cube[:MONTHS_IN_A_YEAR].copy()
    beg_year_tc = beg_year.coord("time")
    beg_year_tc.points = beg_year_tc.points - length_one_year
    if time_coord.has_bounds():
        beg_year_tc.bounds = beg_year_tc.bounds - length_one_year

    # Duplicate the last year.
    length_one_year = time_points[-1] - time_points[-1 - MONTHS_IN_A_YEAR]
    end_year = cube[-MONTHS_IN_A_YEAR:].copy()
    end_year_tc = end_year.coord("time")
    end_year_tc.points = end_year_tc.points + length_one_year
    if time_coord.has_bounds():
        end_year_tc.bounds = end_year_tc.bounds + length_one_year

    # Return a cube with extended years.
    cubelist = iris.cube.CubeList((beg_year, cube, end_year))
    return cubelist.concatenate_cube()


def _extract_baseline_slice(cube, baseline_year):
    """Extract 12 monthly slices for a designated baseline year.

    Args:
        cube (iris.cube.Cube): Source Iris cube.
        baseline_year (int): Calendar year to extract.

    Returns:
        iris.cube.Cube: Slice containing 12 monthly points for
            ``baseline_year``, falling back to the trailing 12 months if the
            year is not explicitly found.
    """
    year_constraint = iris.Constraint(
        time=lambda cell: cell.point.year == baseline_year
    )
    baseline_slice = cube.extract(year_constraint)
    if (
        baseline_slice is None
        or len(baseline_slice.coord("time").points) != MONTHS_IN_A_YEAR
    ):
        raise ValueError(
            f"Baseline year {baseline_year} is missing or does not contain "
            f"{MONTHS_IN_A_YEAR} months in {cube.name()}."
        )
    return baseline_slice.copy()


def tile_constant_years(cube, baseline_year, target_end_year):
    """Extend a monthly time series cube from baseline_year to target_end_year
    by repeating the 12 monthly slices of baseline_year for subsequent years.

    Shifts time points and bounds using cftime year replacement to avoid
    leap-year calendar drift.

    Args:
        cube (iris.cube.Cube): Input monthly time series cube.
        baseline_year (int): Calendar year whose 12 monthly slices are
            replicated.
        target_end_year (int): Terminal calendar year of the extended series.

    Returns:
        iris.cube.Cube: Extended cube tiled to ``target_end_year`` with
            monotonic time bounds.
    """
    if target_end_year <= baseline_year:
        return cube

    baseline_slice = _extract_baseline_slice(cube, baseline_year)
    trimmed_cube = cube.extract(
        iris.Constraint(time=lambda cell: cell.point.year <= baseline_year)
    )
    if trimmed_cube is not None:
        cube = trimmed_cube

    units = cube.coord("time").units
    cubelist = iris.cube.CubeList([cube])

    for y in range(baseline_year + 1, target_end_year + 1):
        year_cube = baseline_slice.copy()
        tc = year_cube.coord("time")
        nyears = y - baseline_year
        tc.points = np.array(
            [
                units.date2num(d.replace(year=d.year + nyears))
                for d in units.num2date(tc.points)
            ],
            dtype=tc.points.dtype,
        )
        if tc.has_bounds():
            tc.bounds = np.array(
                [
                    [
                        units.date2num(b[0].replace(year=b[0].year + nyears)),
                        units.date2num(b[1].replace(year=b[1].year + nyears)),
                    ]
                    for b in units.num2date(tc.bounds)
                ],
                dtype=tc.bounds.dtype,
            )
        cubelist.append(year_cube)

    equalise_attributes(cubelist)
    return cubelist.concatenate_cube()


def _interpolate_months_separately(cube, tpoints):
    """Interpolate to monthly frequency by extracting and interpolating
    separate time series for each month of the year.

    Preserves seasonal cycles by avoiding inter-month smoothing across calendar
    transitions.

    Args:
        cube (iris.cube.Cube): Input Iris cube sampled at multi-year or annual
            intervals.
        tpoints (numpy.ndarray): Target time coordinate sample points.

    Returns:
        iris.cube.Cube: Cube with month-by-month linearly interpolated values
            interleaved.
    """
    new_cube = cube.interpolate([("time", tpoints)], iris.analysis.Linear())
    new_cube.data = np.ma.asarray(new_cube.data)

    # Add month categorisation to extract each month's series
    if not cube.coords("month_number"):
        iris.coord_categorisation.add_month_number(
            cube, "time", name="month_number"
        )

    # Interpolate each month separately and interleave the data
    for m in range(1, MONTHS_IN_A_YEAR + 1):
        month_constraint = iris.Constraint(month_number=m)
        m_cube = cube.extract(month_constraint)
        if m_cube is not None:
            # Select target time points for this month across all years
            m_tpoints = tpoints[m - 1 :: MONTHS_IN_A_YEAR]
            # Interpolate across the years for this month
            m_interpolated = m_cube.interpolate(
                [("time", m_tpoints)], iris.analysis.Linear()
            )
            # Place the interpolated data back
            # into the interleaved target indices
            new_cube.data[m - 1 :: MONTHS_IN_A_YEAR] = m_interpolated.data

    # Clean up month_number coordinate if added
    if cube.coords("month_number"):
        cube.remove_coord("month_number")

    return new_cube


def interpolate_monthly(cube, beg_year, end_year):
    """Interpolate a forcing cube to monthly frequency across a target span
    [beg_year, end_year].

    Applies separate month-by-month linear interpolation to preserve seasonal
    cycles,
    reconstructs continuous cell bounds, and re-inserts exact original slice
    data
    for existing months.

    Args:
        cube (iris.cube.Cube): Source forcing cube.
        beg_year (int): Starting calendar year.
        end_year (int): Ending calendar year.

    Returns:
        iris.cube.Cube: Monthly interpolated Iris cube with 12 time slices per
            year and contiguous monthly coordinate bounds.
    """
    # Get original time units and calendar
    time_coord = cube.coord("time")
    units = time_coord.units
    calendar = units.calendar if units.calendar else "standard"

    # Generate target monthly midpoints and bounds
    tdates = []
    tbounds = []
    for year in range(beg_year, end_year + 1):
        for month in range(1, MONTHS_IN_A_YEAR + 1):
            beg_date = cftime.datetime(year, month, 1, calendar=calendar)
            if month == MONTHS_IN_A_YEAR:
                end_date = cftime.datetime(year + 1, 1, 1, calendar=calendar)
            else:
                end_date = cftime.datetime(
                    year, month + 1, 1, calendar=calendar
                )

            mid_date = beg_date + (end_date - beg_date) / 2
            tdates.append(mid_date)
            tbounds.append([beg_date, end_date])

    tpoints = np.array([units.date2num(d) for d in tdates], dtype=np.float64)
    tbounds_num = np.array(
        [[units.date2num(b[0]), units.date2num(b[1])] for b in tbounds],
        dtype=np.float64,
    )

    # Interpolate each month separately and interleave the data
    new_cube = _interpolate_months_separately(cube, tpoints)

    # Create new DimCoord with contiguous bounds
    new_time_coord = iris.coords.DimCoord(
        tpoints,
        standard_name=time_coord.standard_name,
        long_name=time_coord.long_name,
        var_name=time_coord.var_name,
        units=units,
        bounds=tbounds_num,
        attributes=time_coord.attributes,
    )
    time_dim = cube.coord_dims("time")
    new_cube.remove_coord("time")
    new_cube.add_dim_coord(new_time_coord, time_dim)

    # Overwrite interpolated data with original data for months that exist,
    # matching by the bounds interval (start month and end month).
    # This works only for cubes that already have time bounds.
    if time_coord.has_bounds():
        bounds = time_coord.bounds
        # Map target bounds intervals:
        # (start_year, start_month, end_year, end_month) -> index.
        tbounds_dict = {
            (b[0].year, b[0].month, b[1].year, b[1].month): index
            for index, b in enumerate(tbounds)
        }
        # Ensure data is a writable array (not read-only memmap).
        new_cube.data = np.ma.asarray(new_cube.data)
        for i in range(len(time_coord.points)):
            # Convert original bounds of slice i to date objects.
            beg_date = units.num2date(bounds[i][0])
            end_date = units.num2date(bounds[i][1])
            # Match bounds based on start and end year/month components
            key = (beg_date.year, beg_date.month, end_date.year, end_date.month)
            if key in tbounds_dict:
                target_idx = tbounds_dict[key]
                new_cube.data[target_idx] = cube.data[i]

    return new_cube


def set_coord_system(cube):
    """Assign a standard spherical Earth coordinate system (radius 6371229.0 m)
    to horizontal coordinates.

    Args:
        cube (iris.cube.Cube): Cube to modify in place.
    """
    coord_system = iris.coord_systems.GeogCS(6371229.0)
    cube.coord("latitude").coord_system = coord_system
    cube.coord("longitude").coord_system = coord_system


def fix_coords(args, cube):
    """Align cube horizontal coordinate systems with the target ACCESS-ESM1.5
    grid mask.

    Args:
        args (argparse.Namespace): Parsed CLI arguments containing grid
            configuration.
        cube (iris.cube.Cube): Cube whose latitude and longitude coordinate
            systems will be updated.
    """
    esm_grid_mask = esm_grid_mask_cube(args)
    cube.coord("latitude").coord_system = esm_grid_mask.coord(
        "latitude"
    ).coord_system
    cube.coord("longitude").coord_system = esm_grid_mask.coord(
        "longitude"
    ).coord_system


def fix_poles(cube):
    """Ensure polar values have no longitude dependence by setting them to the
    zonal mean.

    Args:
        cube (iris.cube.Cube): 3D Iris cube with dimensions (time, latitude,
            longitude).
    """
    # Polar values should have no longitude dependence
    latdim = cube.coord_dims("latitude")
    assert latdim == (1,)
    longdim = cube.coord_dims("longitude")
    assert longdim == (2,)
    zonal_mean = np.ma.mean(cube.data, axis=2)
    cube.data[:, 0, :] = zonal_mean[:, [0]]
    cube.data[:, -1, :] = zonal_mean[:, [-1]]


def save_ancil(
    cubes, save_dirpath, save_filename, gregorian=True, replace_bounds=False
):
    """Save one or more Iris cubes to a binary Unified Model (UM) ancillary
    file (.anc).

    Handles both a list and a single cube. Sets the required cube grid
    staggering
    (staggering=3 for New Dynamics) and time attributes.

    To resolve ANTS calendar header omission for monthly fields, writes first
    to
    a temporary directory, uses Mule to inject calendar=1 into the fixed-length
    header,
    and sets model_version to UM vn7.3 (703) to prevent the UM dump format
    warning.

    Args:
        cubes (iris.cube.Cube or list of iris.cube.Cube): Cube(s) to serialize.
        save_dirpath (pathlib.Path): Target directory path.
        save_filename (str): Name of destination .anc file.
        gregorian (bool, optional): If True, sets time_type=1 (Gregorian) and
            converts time coordinates. Defaults to True.
        replace_bounds (bool, optional): If True, reconstructs monthly bounds
            intervals. Defaults to False.
    """
    if not isinstance(cubes, list):
        cubes = [cubes]

    for cube in cubes:
        cube.attributes["grid_staggering"] = 3  # New dynamics
        if gregorian:
            cube.attributes["time_type"] = 1  # Gregorian
            set_gregorian(cube, replace_bounds=replace_bounds)

    ants.__version__ = UM_VERSION
    with tempfile.TemporaryDirectory() as temp_dirname:
        save_temp_pathname = fsdecode(Path(temp_dirname) / save_filename)
        save.ancil(cubes, save_temp_pathname)
        sm = mule.STASHmaster.from_version(UM_VERSION)
        ff = mule.AncilFile.from_file(save_temp_pathname, stashmaster=sm)
        ff.fixed_length_header.calendar = 1
        # Ensure that the directory exists.
        save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
        save_file_pathname = fsdecode(save_dirpath / save_filename)
        ff.to_file(save_file_pathname)
