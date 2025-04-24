# Use mule to create ozone ancillary file from netcdf
# Assumes zonal mean ozone

import mule, netCDF4, sys, f90nml, argparse, types
import numpy as np
import validate_ancil

parser = argparse.ArgumentParser(description='Convert ozone netCDF file to ancillary')

parser.add_argument('--vertlevs', dest='vertlevs',
                    default='/projects/access/umdir/vn7.3/ctldata/vert/vertlevs_G3',
                    help = 'UM vertical levels namelist file')
parser.add_argument('-c', '--climatology', dest='climatology',
                    action='store_true', default=False,
                    help='Create periodic 12 month climatology')
parser.add_argument('-f', '--firstyr', dest='firstyr', type=int,
                    default=None, required=False,
                    help='First year of data (required if not climatology)')
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

f = netCDF4.Dataset(args.input)

levels = f90nml.read(args.vertlevs)

eta_theta_levels = np.array(levels['vertlevs']['eta_theta'])
eta_rho_levels = np.array(levels['vertlevs']['eta_rho'])
z_top_of_model = levels['vertlevs']['z_top_of_model']
# Add one to match fortran indexing here
first_constant_r_rho_level = levels['vertlevs']['first_constant_r_rho_level']

r_theta_levels = eta_theta_levels * z_top_of_model
r_rho_levels = eta_rho_levels * z_top_of_model
# orography term
C_theta = np.zeros(len(eta_theta_levels))
C_rho = np.zeros(len(eta_rho_levels))
for k in range(first_constant_r_rho_level):
    # use first_constant_r_rho_level-1 because it's a fortran index
    C_rho[k] = (1.0 - eta_rho_levels[k]/eta_rho_levels[first_constant_r_rho_level-1])**2
    C_theta[k] = (1.0 - eta_theta_levels[k]/eta_rho_levels[first_constant_r_rho_level-1])**2

o3 = f.variables['o3']

n_times, n_levs, n_rows = o3.shape[:]
n_cols = 1  # Zonal mean

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
        'num_levels': n_levs,
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
    'level_dependent_constants':{
        # Need to have an extra level here
        'dims': (n_levs + 1, None),
        'eta_at_theta': np.array(levels['vertlevs']['eta_theta'][:]),
        'eta_at_rho': np.concatenate([np.array(levels['vertlevs']['eta_rho']), [-2.**30]]),
        }
    }

new_ff = mule.AncilFile.from_template(template)

if args.climatology:
    new_ff.fixed_length_header.t1_year = 0
    new_ff.fixed_length_header.t2_year = 0
    new_ff.fixed_length_header.time_type = 2
    if n_times != 12:
        print("Error - for climatology input file must have 12 monthly values")
        sys.exit(1)

for m in range(n_times):
    for k in range(n_levs):

        new_field = mule.Field2.empty()

        # To correspond to the header-release 3 class used
        new_field.lbrel = 2

        # Several of the settings can be copied from the file object
        new_field.lbnpt = new_ff.integer_constants.num_cols
        new_field.lbrow = new_ff.integer_constants.num_rows

        new_field.bdx = new_ff.real_constants.col_spacing
        new_field.bdy = new_ff.real_constants.row_spacing

        new_field.bzx = new_ff.real_constants.start_lon
        new_field.bzy = new_ff.real_constants.start_lat - new_ff.real_constants.row_spacing
        new_field.bplon = 0.
        new_field.bplat = 90.

        new_field.lbcode = 1
        new_field.lbhem = 0  # Global
        new_field.lbpack = 2
        new_field.lbuser1 = 1  # Real field
        new_field.lbuser4 = 60  # Ozone
        new_field.lbuser7 = 1

        new_field.lbhr = 0
        new_field.lbmin = 0
        new_field.lbsec = 0
        new_field.lbday =  0
        new_field.lbhrd = 0
        new_field.lbmind = 0
        new_field.lbsecd = 0
        new_field.lbtim = 1 # Gregorian calendar
        new_field.lbft = 0
        new_field.lbext = 0
        new_field.lbfc = 453 # Field code for ozone
        new_field.lbcfc = 0
        new_field.lbvc = 65 # Hybrid height vertical coordinate
        new_field.lbrfc = 0
        new_field.lbexp = 0
        new_field.lbproj = 0
        new_field.lbtyp = 0
        new_field.lbsrvd1 = new_field.lbsrvd2 = new_field.lbsrvd3 = new_field.lbsrvd4 = 0
        new_field.lbsrce = 7031111
        new_field.lbproc = 192  # Time mean + zonal mean

        new_field.lblev = k+1
        new_field.lbdat = new_field.lbdatd = 16 
        # To match the CMIP5 SPARC data
        new_field.lbday = new_field.lbdayd = 16 + 30 * (m%12)
        new_field.lbyr = firstyr + m//12
        new_field.lbyrd = firstyr + m//12
        new_field.lbmon = m%12+1
        new_field.lbmond = m%12+1
        new_field.blev = r_theta_levels[k+1]
        new_field.bhlev = C_theta[k+1]
        new_field.bmdi = -2.**30
        if k==0:
            # This matches existing vn 7.3 ozone file
            new_field.brlev = 0.
            new_field.bhrlev = 1.
        else:
            new_field.brlev = r_rho_levels[k]
            new_field.bhrlev = C_rho[k]
        data_array = o3[m,k]
        data_array.shape = (n_rows, n_cols)
        array_provider = mule.ArrayDataProvider(data_array)
        new_field.set_data_provider(array_provider)
        new_ff.fields.append(new_field)

# Override the standard validator with one that adds an extra value
# to level dependent constants.
# https://stackoverflow.com/questions/394770/override-a-method-at-instance-level
new_ff.validate = types.MethodType(validate_ancil.validate_ancil, new_ff)
new_ff.to_file(args.output)
