import calendar

import mule
from cmip7_ancil_common import cmip7_date_constraint_from_years
from cmip7_ancil_constants import UM_VERSION

CMIP7_PI_YEAR = 1850
DAYS_IN_CMIP7_PI_YEAR = 365.0


def cmip7_pi_date_constraint():
    return cmip7_date_constraint_from_years(CMIP7_PI_YEAR, CMIP7_PI_YEAR)


def fix_esm15_pi_ancil_date(ifile, ofile):
    """
    Correct the dates of the ESM1.5 preindustrial ancillaries
    so that they can be read by Iris.
    These have field end dates appropriate to the 360 day calendar
    rather than Gregorian. Also reset the year number to CMIP7_PI_YEAR.
    """

    sm = mule.STASHmaster.from_version(UM_VERSION)
    ff = mule.AncilFile.from_file(ifile, stashmaster=sm)

    # Should not be included in an ancillary file. Flagged by mule validation
    ff.level_dependent_constants = None

    ff.fixed_length_header.t1_year = CMIP7_PI_YEAR
    ff.fixed_length_header.t2_year = CMIP7_PI_YEAR

    for field in ff.fields:
        field.lbyr = field.lbyrd = CMIP7_PI_YEAR
        # Correct end of month
        field.lbdatd = calendar.monthrange(CMIP7_PI_YEAR, field.lbmon)[1]

    ff.to_file(ofile)
