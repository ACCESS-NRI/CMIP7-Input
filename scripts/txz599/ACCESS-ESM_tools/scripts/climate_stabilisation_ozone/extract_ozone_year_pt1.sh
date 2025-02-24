#!/bin/bash
#module purge
module use ~access/modules
module load ants/0.11.0
module load cdo
module load nco
set -a

year=2055
outfile=ozone_${year}_ssp585_ESM1

timeserfile=1850/ozone_2014_2101_ssp585_ESM1.anc
templatefile=1850/ozone_1850_ESM1_v2.anc

echo "creating fixed ozone: $outfile"
mkdir -p $year

echo "replacing template data with ${year} data"
python -W ignore py/cov_ozone_replace-year.py
