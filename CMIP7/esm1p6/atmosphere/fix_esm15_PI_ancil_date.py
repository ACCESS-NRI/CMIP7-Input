import calendar
import mule
import sys
from cmip7_ancil_constants import * 

def fix_esm15_PI_ancil_date(ifile, ofile):
    """
    Correct the dates of the ESM1.5 1850 ancillaries so that they can be read by Iris.
    These have field end dates appropriate to the 360 day calendar rather than Gregorian.
    Also reset the year number to 1850.
    """

    sm = mule.STASHmaster.from_version(UM_VERSION)
    ff = mule.AncilFile.from_file(ifile, stashmaster=sm)
    
    # Should not be included in an ancillary file. Flagged by mule validation
    ff.level_dependent_constants = None
    
    ff.fixed_length_header.t1_year = 1850
    ff.fixed_length_header.t2_year = 1850
    
    for field in ff.fields:
        field.lbyr = field.lbyrd = 1850
        # Correct end of month
        field.lbdatd = calendar.monthrange(1850, field.lbmon)[1]
    
    ff.to_file(ofile)
