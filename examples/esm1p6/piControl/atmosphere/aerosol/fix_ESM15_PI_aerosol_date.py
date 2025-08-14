# Correct the dates of the ESM1.5 1850 ancillaries so that they can be read by iris
# These have field end dates appropriate to the 360 day calendar rather than Gregorian
# Also reset the year number to 1850

import mule, sys, calendar

ifile = sys.argv[1]
ofile = sys.argv[2]

ff = mule.AncilFile.from_file(ifile)

# Should not be included in an ancillary file. Flagged by mule validation
ff.level_dependent_constants = None

ff.fixed_length_header.t1_year = 1850
ff.fixed_length_header.t2_year = 1850

for field in ff.fields:
    field.lbyr = field.lbyrd = 1850
    # Correct end of month
    field.lbdatd = calendar.monthrange(1850, field.lbmon)[1]

ff.to_file(ofile)
