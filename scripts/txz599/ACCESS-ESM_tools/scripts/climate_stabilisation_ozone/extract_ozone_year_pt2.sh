#!/bin/bash
#module purge
module use ~access/modules
module use /g/data/hh5/public/modules
module load pythonlib/mule/2017.8.1
module load pythonlib/netCDF4/1.5.3
module load pythonlib/f90nml
set -a

year=2055
outfile=ozone_${year}_ssp585_ESM1

echo "creating ancil"
python py/ozone_ancil.py -c ${year}/${outfile}_tmp.nc ${year}/$outfile.anc
rm ${year}/${outfile}_tmp.nc
