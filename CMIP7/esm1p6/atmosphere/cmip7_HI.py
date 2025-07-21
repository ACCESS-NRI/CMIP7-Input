from cmip7_ancil_constants import UM_VERSION

import calendar
import cftime
import iris
import mule

CMIP7_HI_BEG_YEAR = 1849
CMIP7_HI_END_YEAR = 2015

# For CMIP6 and CMIP7 data
CMIP7_HI_BEG_DATE = cftime.DatetimeNoLeap(CMIP7_HI_BEG_YEAR, 1, 1)
CMIP7_HI_END_DATE = cftime.DatetimeNoLeap(CMIP7_HI_END_YEAR, 12, 31)
CMIP7_HI_DATE_CONSTRAINT = iris.Constraint(
    time=lambda cell: CMIP7_HI_BEG_DATE <= cell.point <= CMIP7_HI_END_DATE)


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
