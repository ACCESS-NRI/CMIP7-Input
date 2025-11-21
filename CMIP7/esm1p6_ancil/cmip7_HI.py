import calendar
from pathlib import Path

import mule

from .cmip7_ancil_constants import ANCIL_TODAY, UM_VERSION
from .cmip7_PI import CMIP7_PI_YEAR

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
