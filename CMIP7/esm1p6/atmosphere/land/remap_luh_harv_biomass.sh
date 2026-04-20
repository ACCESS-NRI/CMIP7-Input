#!/bin/bash
#PBS -P p66
#PBS -q normal
#PBS -l walltime=00:20:00
#PBS -l ncpus=4
#PBS -l mem=64GB
#PBS -l storage=gdata/p66+gdata/qv56+gdata/fs38

# Remap the LUH3 wood harvest data onto the ACCESS-ESM1.6 grid

module load cdo

WD="/g/data/p66/ajn563/ACCESS-ESM/ESM1.6/luh3-1-1"

cd "$WD"

# Specify location of input files
INFILE=/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/UofMD/UofMD-landState-3-1-1/land/yr/multiple-transitions/gn/v20250325/multiple-transitions_input4MIPs_landState_CMIP_UofMD-landState-3-1-1_gn_0850-2023.nc
ACCESS_LAND_SEA_FRAC=/g/data/fs38/publications/CMIP6/CMIP/CSIRO/ACCESS-ESM1-5/historical/r1i1p1f1/fx/sftlf/gn/latest/sftlf_fx_ACCESS-ESM1-5_historical_r1i1p1f1_gn.nc

# Make land-sea mask.
cdo -gtc,0 $ACCESS_LAND_SEA_FRAC mask.nc

# Add relevant LUH3 variables together
cdo -L remapcon,ACCESS.grid\
    -add -add -add -add -add \
        -selname,primf_bioh $INFILE \
	-selname,secmf_bioh $INFILE \
        -selname,secyf_bioh $INFILE \
	-selname,primn_bioh $INFILE \
	-selname,secnf_bioh $INFILE \
        -selname,pltns_bioh $INFILE \
    temp1.nc

# Keep ACCESS land points, and set missing-on-land to 0
cdo -L -ifthen mask.nc -setmisstoc,0 temp1.nc temp3.nc

# Name + metadata
cdo -L -setname,bioh temp3.nc harvest_bioh_primfonly.nc
ncatted -O -a long_name,bioh,m,c,"wood harvest biomass carbon" harvest_bioh_primfonly.nc
ncatted -O -a comment,bioh,m,c,"wood harvest biomass carbon summed over LUH3 data variable 'primf_bioh'" harvest_bioh_primfonly.nc
ncatted -O -a history,bioh,d,, harvest_bioh_primfonly.nc

# Clean up
rm -f temp1.nc temp3.nc mask.nc
