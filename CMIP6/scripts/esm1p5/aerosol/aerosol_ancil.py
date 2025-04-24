# Use mule to create aerosol ancillary file from netcdf
# Monthly mean time dependent
# Time values in netcdf file are completely wrong,

from __future__ import division, print_function
import mule, netCDF4, sys, argparse
import numpy as np

parser = argparse.ArgumentParser(description='Convert aerosol netCDF file to ancillary')
parser.add_argument('-c', '--climatology', dest='climatology',
                    action='store_true', default=False,
                    help='Create periodic 12 month climatology')
parser.add_argument('-f', '--firstyr', dest='firstyr', type=int,
                    default=None, required=False,
                    help='First year of data (required if not climatology)')
parser.add_argument('--vars', dest='vars', nargs = '+', required=True,
                    help = 'List of variable names from netCDF file')
parser.add_argument('--stash', dest='stash', type=int, nargs = '+', required=True,
                    help = 'List of stash codes matching variable name list')

parser.add_argument('input', help='Input netCDF file')
parser.add_argument('output', help='Output ancillary file')
args = parser.parse_args()

if not args.climatology and not args.firstyr:
    print("Error - first year not set")
    sys.exit(1)
if args.climatology:
    firstyr = 0
else:
    firstyr = args.firstyr

# Black carbon {'field573':129}
# OCFF  {'field573':135}
# Biomass {'field574':130, 'field574_1':131}
# Field codes for aerosol emissions (from stashmaster)
fldcode = {58:569, 59:570, 121:569, 126:569, 127:572, 128:573,
           129:573, 130:574, 131:574, 134:573, 135:573}

print("Processing", list(zip(args.vars, args.stash)))

f = netCDF4.Dataset(args.input)

aero = f.variables[args.vars[0]]

# Field has a dummy surface dimension
n_times, surface, n_rows, n_cols = aero.shape[:]

n_levs = 38

template = {
    'fixed_length_header':{
        'data_set_format_version': 20,  # Always fixed
        'sub_model': 1,                 # Atmosphere
        'vert_coord_type': 1,           # Hybrid heights
        'horiz_grid_type': 0,           # Global file
        'dataset_type': 4,              # Ancillary
        'calendar' : 1,                 # Gregorian
        'grid_staggering': 3,           # ND
        'time_type' : 1,                # Time series
        'model_version': 703,
        't1_year' : firstyr,
        't1_month' : 1,
        't1_day' : 16,
        't1_hour' : 0,
        't1_minute' : 0,
        't1_second' : 0,
        't1_year_day_number' : 0,
        't2_year' : firstyr + (n_times//12)-1,
        't2_month' : 12,
        't2_day' : 16,
        't2_minute' : 0,
        't2_second' : 0,
        't2_year_day_number' : 0,
        't3_year' : 0,
        't3_month' : 1,
        't3_day' : 0,
        't3_minute' : 0,
        't3_second' : 0,
        't3_year_day_number' : 0,
        },
    'integer_constants':{
        'num_times' : n_times,
        'num_levels': 1,
        'num_cols': n_cols,
        'num_rows': n_rows
        },
    'real_constants':{
        'col_spacing': 360.0/n_cols,
        'row_spacing': 180.0/(n_rows-1),
        'start_lat': -90.0,
        'start_lon': 0.0,
        'north_pole_lat': 90.0,
        'north_pole_lon': 0.0,
        },
    }

new_ff = mule.AncilFile.from_template(template)

if args.climatology:
    new_ff.fixed_length_header.t1_year = 0
    new_ff.fixed_length_header.t2_year = 0
    new_ff.fixed_length_header.time_type = 2
    if n_times != 12:
        print("Error - for climatology input file must have 12 monthly values")
        sys.exit(1)

new_ff.level_dependent_constants = \
    mule.ancil.Ancil_LevelDependentConstants.empty(new_ff.integer_constants.num_levels)

for m in range(n_times):

    for vname, stash in zip(args.vars, args.stash):
        aero = f.variables[vname]

        new_field = mule.Field2.empty()

        # To correspond to the header-release 3 class used
        new_field.lbrel = 2

        # Several of the settings can be copied from the file object
        new_field.lbnpt = new_ff.integer_constants.num_cols
        new_field.lbrow = new_ff.integer_constants.num_rows

        new_field.bdx = new_ff.real_constants.col_spacing
        new_field.bdy = new_ff.real_constants.row_spacing

        new_field.bzx = new_ff.real_constants.start_lon -new_ff.real_constants.col_spacing
        new_field.bzy = new_ff.real_constants.start_lat - new_ff.real_constants.row_spacing
        new_field.bplon = 0.
        new_field.bplat = 90.

        new_field.lbcode = 1
        new_field.lbhem = 0  # Global
        new_field.lbpack = 2
        new_field.lbuser1 = 1  # Real field
        new_field.lbuser4 = stash
        new_field.lbuser7 = 1

        new_field.lbdat = 1
        new_field.lbhr = 0
        new_field.lbmin = 0
        new_field.lbsec = 0
        new_field.lbday =  0
        new_field.lbdatd = 30
        new_field.lbhrd = 0
        new_field.lbmind = 0
        new_field.lbsecd = 0
        new_field.lbtim = 1 # Gregorian calendar
        new_field.lbft = 0
        new_field.lbext = 0
        if stash in fldcode:
            new_field.lbfc = fldcode[stash]
        else:
            new_field.lbfc = 0
        new_field.lbcfc = 0
        new_field.lbvc = 0
        new_field.lbrvc = 0
        new_field.lbexp = 0
        new_field.lbproj = 0
        new_field.lbtyp = 0
        new_field.lbrsvd1 = new_field.lbrsvd2 = new_field.lbrsvd3 = new_field.lbrsvd4 = 0
        new_field.lbsrce = 7031111
        new_field.lbproc = 192  # Time mean + zonal mean

        new_field.lblev = 0
        new_field.lbuser5 = 0
        new_field.lbyr = firstyr + m//12
        new_field.lbyrd = firstyr + m//12
        new_field.lbmon = m%12+1
        new_field.lbmond = m%12+1
        new_field.blev = 0.
        new_field.bhlev = 0.
        new_field.brlev = 0.
        new_field.bhrlev = 0.
        new_field.bmdi = -2.**30
        # Masked out at N-most latitude. Set this to zero.
        if isinstance(aero[m],np.ma.MaskedArray):
            data_array = aero[m].filled(0)
        else:
            data_array = aero[m]
        data_array.shape = (n_rows, n_cols)
        array_provider = mule.ArrayDataProvider(data_array)
        new_field.set_data_provider(array_provider)
        new_ff.fields.append(new_field)

new_ff.to_file(args.output)
