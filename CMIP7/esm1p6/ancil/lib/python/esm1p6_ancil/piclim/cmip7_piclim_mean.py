
# Create files for input to Taylor step of ESM1.6 CMIP ancillary workflow
# This expects PP file format

from argparse import ArgumentParser
import cf_units, cftime
import iris, iris.coord_categorisation
import numpy as np
from pathlib import Path

def fixatts(cube, field, filename):
    # Remove the attributes that prevent concatenation
    for attr in ['date_created', 'date_metadata_modified', 'date_modified', 'filename', 'history']:
        del cube.attributes[attr]

def process(varname, ppfilename, args):
    # Need to use load and concatenate rather than load_cube because merge doesn't work
    # with existing time dimensions
    # Only the output directory numbers matter, not the year numbers so use glob
    iris.FUTURE.datum_support = True # To suppress warnings
    files = [ list(args.cmip7_picontrol_archive.glob(f'output{i:03d}/atmosphere/access-esm1p6.um7p3.2d.{varname}.1mon.mean.*.nc'))[0]
                   for i in range(args.cmip7_picontrol_output_start, args.cmip7_picontrol_output_end+1) ]
    var = iris.load(files, callback=fixatts).concatenate_cube()

    # Calculate mean annual cycle
    iris.coord_categorisation.add_month_number(var, coord='time', name='month')
    var_mean = var.aggregated_by('month', iris.analysis.MEAN)

    # Probably not necessary
    var_mean.data = var_mean.data.filled(0.)

    # New time axis to create a longer file to match the input4MIPS time, 1870-2022
    taxis = cf_units.Unit("days since 1870-01-01 00:00", calendar='gregorian')
    nyr = 153
    tvals = np.zeros(nyr*12)
    tbnds = np.zeros((nyr*12,2))

    _, nlat, nlon = var.shape
    newvar = np.zeros((nyr*12,nlat,nlon), np.float32)

    i = 0
    for y in range(1870, 1870+nyr):
        for m in range(1,13):
            tbnds[i,0] = taxis.date2num(cftime.DatetimeProlepticGregorian(y, m, 1, 0, 0, 0))
            if m==12:
                tbnds[i,1] = taxis.date2num(cftime.DatetimeProlepticGregorian(y+1, 1, 1, 0, 0, 0))
            else:
                tbnds[i,1] = taxis.date2num(cftime.DatetimeProlepticGregorian(y, m+1, 1, 0, 0, 0))
            tvals[i] = 0.5*(tbnds[i,0]+tbnds[i,1])
            newvar[i] = var_mean.data[m-1]
            i += 1

    timedim = iris.coords.DimCoord(tvals, bounds=tbnds, units=taxis, standard_name='time')
    newvar = iris.cube.Cube(newvar, dim_coords_and_dims=[(timedim,0), (var.coord('latitude'),1), (var.coord('longitude'),2)])

    # Ensure that the directory exists.
    args.share_dirname.mkdir(mode=0o755, parents=True, exist_ok=True)
    # Save as a PP file
    iris.save(newvar, args.share_dirname / ppfilename)


if __name__ == "__main__":
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--share-dirname', type=Path, required=True)
    parser.add_argument('--mask-dirname')
    parser.add_argument('--cmip7-picontrol-archive', type=Path, required=True)
    parser.add_argument('--cmip7-picontrol-output-start', type=int, required=True)
    parser.add_argument('--cmip7-picontrol-output-end', type=int, required=True)
    args = parser.parse_args()
    process('fld_s00i507', 'sst_amip_regridded_n96.pp', args) # SST
    process('fld_s00i031', 'seaice_amip_regridded_n96.pp', args) # Sea ice concentration
