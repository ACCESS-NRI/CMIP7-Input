import calendar
from pathlib import Path

import iris
import mule
from cmip7_ancil_constants import (
    ANCIL_TODAY,
    MONTHS_IN_A_YEAR,
    UM_VERSION,
)
from cmip7_PI import CMIP7_PI_YEAR

CMIP7_HI_BEG_YEAR = CMIP7_PI_YEAR
CMIP7_HI_END_YEAR = 2022
CMIP7_HI_NBR_YEARS = CMIP7_HI_END_YEAR + 1 - CMIP7_HI_BEG_YEAR


def esm_hi_forcing_save_dirpath(args):
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "historical"
        / "atmosphere"
        / "forcing"
        / "resolution_independent"
        / ANCIL_TODAY
    )


def fix_esm15_hi_ancil_date(ifile, ofile):
    """
    Correct the dates of the ESM1.5 historical ancillaries
    so that they can be read by Iris.
    These have field end dates appropriate to the 360 day calendar
    rather than Gregorian.
    """

    sm = mule.STASHmaster.from_version(UM_VERSION)
    ff = mule.AncilFile.from_file(ifile, stashmaster=sm)

    # Should not be included in an ancillary file. Flagged by mule validation
    ff.level_dependent_constants = None

    for field in ff.fields:
        # Correct end of month
        field.lbdatd = calendar.monthrange(field.lbyr, field.lbmon)[1]

    ff.to_file(ofile)


def extend_hi_years(cube):
    """
    Extend a cube representing a monthly time series by duplicating
    and adjusting the first and last years.
    Based on Crown copyright code from ozone_cmip6_ancillary_for_suite.py
    by Steven Hardiman of the UK Met Office.
    """
    time_coord = cube.coord("time")
    time_points = time_coord.points
    if (months := len(time_points)) <= MONTHS_IN_A_YEAR:
        raise ValueError(
            f"Cannot extend a cube containing {months} months of data. "
            f"More than {MONTHS_IN_A_YEAR} months are required."
        )

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
