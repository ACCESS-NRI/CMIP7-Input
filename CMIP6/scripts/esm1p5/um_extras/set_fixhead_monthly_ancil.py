# Set ancillary file validity time appropriate for monthly mean
# data

from um_fileheaders import *
import umfile, sys

print sys.argv[1]
f = umfile.UMFile(sys.argv[1], 'r+')

f.fixhd[FH_CTYear]  = 0
f.fixhd[FH_CTMonth]   = 1
f.fixhd[FH_CTDay]     = 0
f.fixhd[FH_CTHour]    = 0
f.fixhd[FH_CTMinute]  = 0
f.fixhd[FH_CTSecond]  = 0
f.fixhd[FH_CTDayNo]   = 0

f.close()
