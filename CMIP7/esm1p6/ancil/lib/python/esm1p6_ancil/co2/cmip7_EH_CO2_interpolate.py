'''
This script interpolates CMIP7 historical emissions CO2 data to the ESM1.6 grid and saves the result as an ancillary file.
It loads the CMIP7 historical emissions CO2 data, aggregates the sector and altitude dimensions, regrids the data to match the ESM1.6 grid, and saves the result as an ancillary file.
The output is saved in the specified directory path.
'''

# Interpolate CMIP7 EH CO2 emissions to ESM1.6 grid
from pathlib import Path

import iris
from aerosol.cmip7_aerosol_common import zero_poles
from aerosol.cmip7_HI_aerosol_anthro import (
    load_cmip7_hi_aerosol_air_anthro,
    load_cmip7_hi_aerosol_anthro,
    parse_args,
)
from cmip7_ancil_common import (
    INTERPOLATION_SCHEME,
    esm_grid_mask_cube,
    save_ancil,
)
from cmip7_ancil_constants import ANCIL_TODAY
from cmip7_HI import CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR

SPECIES = "CO2"
STASH_ITEM = 251
# The CO2 time series includes 1849 and 2023,
# so use these years directly from the datasets.
CMIP7_HI_CO2_BEG_YEAR = CMIP7_HI_BEG_YEAR - 1
CMIP7_HI_CO2_END_YEAR = CMIP7_HI_END_YEAR + 1


def esm_eh_co2_save_dirpath(args):
    '''
    Return the directory path to save the ESM1.6 EH CO2 emissions ancil file.
    '''
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / "historical-emissions"
        / "atmosphere"
        / "forcing"
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )


def cmip7_eh_co2_anthro_interpolate(args):
    """
    Interpolate CMIP7 historical emissions CO2 data to the ESM1.6 grid.
    """
    # Load the CMIP7 historical emissions CO2 data. 
    cube = load_cmip7_hi_aerosol_anthro(
        args,
        SPECIES,
        beg_year=CMIP7_HI_CO2_BEG_YEAR,
        end_year=CMIP7_HI_CO2_END_YEAR,
    )
    
    # Aggregate the sector dimension by summing all sector contributions into a single field
    cube_sum = cube.collapsed(["sector"], iris.analysis.SUM)

    # Load the air emissions data for CO2 from the CMIP7 historical emissions dataset.
    cube_air = load_cmip7_hi_aerosol_air_anthro(
        args,
        SPECIES,
        beg_year=CMIP7_HI_CO2_BEG_YEAR,
        end_year=CMIP7_HI_CO2_END_YEAR,
    )

    # Aggregate the altitude dimension by summing all altitude contributions into a single field
    cube_air_sum = cube_air.collapsed(["altitude"], iris.analysis.SUM)
    # Combine the two cubes to get the total CO2 emissions, including both surface and air contributions.
    cube_tot = cube_sum + cube_air_sum

    # Regrid the combined emissions field onto the ESM1.6 grid mask.
    esm_cube = cube_tot.regrid(esm_grid_mask_cube(args), INTERPOLATION_SCHEME)
    # Fill any missing data with zeros.
    esm_cube.data = esm_cube.data.filled(0.0)
    # Ensure that the poles are set to zero as well
    zero_poles(esm_cube)
    # Set the STASH item for the output cube so that it can be correctly identified in the ESM1.6 model.
    esm_cube.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=STASH_ITEM
    )

    save_dirpath = esm_eh_co2_save_dirpath(args)
    # Save the regridded CO2 emissions data as an ancillary file in the specified directory.
    save_ancil(esm_cube, save_dirpath, args.save_filename)


if __name__ == "__main__":
    '''
    Interpolate CMIP7 historical emissions CO2 data to the ESM1.6 grid and save as an ancillary file.
    '''

    # Parse command line arguments for the script.
    args = parse_args(species=SPECIES)

    # Perform the interpolation and save the result.
    cmip7_eh_co2_anthro_interpolate(args)
