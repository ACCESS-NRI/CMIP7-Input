#!/usr/bin/env python

# Replace a field in a UM fieldsfile with values from a netcdf file
# Note that this modifies the file in place
# Multi-level field may be physical levels or pseudo-dimension like
# vegetation types.

# Martin Dix martin.dix@csiro.au

import numpy as np
import argparse, sys
import umfile
from um_fileheaders import *
import cdms2
from cdms2 import MV2


parser = argparse.ArgumentParser(description="Replace field in UM file with a field from a netCDF file.")
parser.add_argument('-v', dest='varcode', type=int, required=True, help='Variable to be replaced (specified by STASH index = section_number * 1000 + item_number')
parser.add_argument('-n', dest='ncfile', required=True, help='Input netCDF file')
parser.add_argument('-V', dest='ncvarname', required=True, help='netCDF variable name')
parser.add_argument('target', help='UM File to change')


args = parser.parse_args()

d = cdms2.open(args.ncfile)
try:
    # Remove singleton dimensions (time or level in surface fields)
    ncvar = d.variables[args.ncvarname](squeeze=1)
except KeyError:
    print "\nError: variable %s not in %s" % (args.ncvarname, args.ncfile)
    sys.exit(1)
    

f = umfile.UMFile(args.target, "r+")

# Set new missing value to match the UM missing value 
arr = MV2.array(ncvar[:])
arr.setMissing(f.missval_r)

assert len(arr.shape)==3, 'Expected 3D netCDF input'

# Loop over all the fields
replaced = False
ilev=1
for k in range(f.fixhd[FH_LookupSize2]):
    ilookup = f.ilookup[k]
    lbegin = ilookup[LBEGIN] # lbegin is offset from start
    if lbegin == -99:
        break
    if ilookup[ITEM_CODE] == args.varcode:
        print "Replacing field", k, ilookup[ITEM_CODE], ilev
        # Check the levels match
        if not (ilookup[LBLEV] == ilev or
                ilookup[LBLEV] == 9999 and ilookup[LBPLEV] == ilev):
            print 'Level mismatch'
            sys.exit(1)
        # Simplest way to get 32/64 bit size right, though umfile
        # should really fix it on write
        a = f.readfld(k)
        if not a.shape == arr.shape[1:]:
            print "\nError: grid shape mismatch"
            print "UM grid shape", a.shape
            print "netcdf field shape", arr.shape
            sys.exit(1)
        a[:] = arr[ilev-1]
        ilev += 1
        f.writefld(a[:], k)
        replaced = True

if not replaced:
    print "\nWarning: requested stash code %d not found in file %s" % (args.varcode, args.target)
    print "No replacement made."

f.close()
