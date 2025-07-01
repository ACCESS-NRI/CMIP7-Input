from aerosol.cmip7_aerosol_common import *

CMIP7_AEROSOL_ANTHRO_VERSION = os.environ['CMIP7_AEROSOL_ANTHRO_VERSION']
CMIP7_AEROSOL_ANTHRO_VDATE = os.environ['CMIP7_AEROSOL_ANTHRO_VDATE']

def cmip7_aerosol_anthro_base(version):
    return Path(CMIP7_SOURCE_DATA / 'PNNL-JGCRI' / version / 'atmos/mon')

def cmip7_aerosol_anthro_path(species, version, vdate):
    base = cmip7_aerosol_anthro_base(version)
    filename = f'{species}-em-anthro_input4MIPs_emissions_CMIP_{version}_gn_185001-189912.nc' 
    return base / f'{species}_em_anthro' / 'gn' / vdate / filename

def load_cmip7_aerosol_anthro(species, version, vdate, constraint):
    cube = iris.load_cube(cmip7_aerosol_anthro_path(species, version, vdate), constraint)
    fix_coords(cube)
    return cube

def load_cmip7_aerosol_anthro_1850(species):
    return load_cmip7_aerosol_anthro(
            species, 
            CMIP7_AEROSOL_ANTHRO_VERSION, 
            CMIP7_AEROSOL_ANTHRO_VDATE, 
            constraint_1850)

def cmip7_aerosol_anthro_interpolate(species, stash_item, ancil_filename):
    cube = load_cmip7_aerosol_anthro_1850('BC')
    cube_tot = cube.collapsed(['sector'], iris.analysis.SUM)
    esm16_cube = cube_tot.regrid(mask_esm15, interpolation_scheme)
    esm16_cube.data = esm16_cube.data.filled(0.)
    zero_poles(esm16_cube)
    esm16_cube.attributes['STASH'] = iris.fileformats.pp.STASH(model=1, section=0, item=stash_item)
    save_ancil(esm16_cube, cmip7_aerosol_save_path(ancil_filename))
