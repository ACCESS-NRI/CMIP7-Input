from cmip7_ancil_constants import UM_VERSION

import calendar
import mule


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
