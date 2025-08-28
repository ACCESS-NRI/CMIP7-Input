from argparse import ArgumentParser
from pathlib import Path

import f90nml
import iris
import numpy as np
from cmip7_ancil_argparse import dataset_parser, path_parser
from ghg.cmip7_ghg import (
    GHG_MOLAR_MASS,
    cmip7_ghg_dirpath,
    cmip7_ghg_filename,
    cmip7_ghg_mmr,
    cmip7_pro_greg_date_constraint_from_years,
)

CMIP7_GHG_HI_BEG_YEAR = 1850
CMIP7_GHG_HI_END_YEAR = 2022
CMIP7_GHG_HI_NBR_YEARS = CMIP7_GHG_HI_END_YEAR + 1 - CMIP7_GHG_HI_BEG_YEAR


def parse_args():
    parser = ArgumentParser(
        parents=[path_parser(), dataset_parser()],
        prog='cmip7_HI_ghg_generate',
        description=(
            'Generate input files from CMIP7 historical greenhouse gas forcings'
        ),
    )
    parser.add_argument('--dataset-date-range')
    return parser.parse_args()


def load_cmip7_hi_ghg_mmr(args, ghg):
    cmip7_filepath = cmip7_ghg_dirpath(args, ghg) / cmip7_ghg_filename(
        args, ghg
    )

    # Read in the CMIP7 cube.
    full_cube = iris.load_cube(cmip7_filepath)

    # Check that we have the right greenhouse gas.
    variable_id = full_cube.metadata.attributes['variable_id']
    assert ghg == variable_id

    # Extract the historical years.
    date_constraint = cmip7_pro_greg_date_constraint_from_years(
        CMIP7_GHG_HI_BEG_YEAR, CMIP7_GHG_HI_END_YEAR
    )
    hi_cube = full_cube.extract(date_constraint)

    # Determine the mass mixing ratio.
    ghg_mmr_list = []
    for year in range(CMIP7_GHG_HI_BEG_YEAR, CMIP7_GHG_HI_END_YEAR + 1):
        year_constraint = cmip7_pro_greg_date_constraint_from_years(year, year)
        year_cube = hi_cube.extract(year_constraint)
        ghg_mmr_list.append(cmip7_ghg_mmr(year_cube, ghg))
    return ghg_mmr_list


def cmip7_hi_ghg_patch(ghg_mmr_dict):
    """
    Patch the greenhouse gas variables in the clmchfcg namelist
    """
    # Map each greenhouse gas to an index in the
    # historical climate forcing arrays.
    GHG_HI_NAMELIST_INDEX = {
        'cfc11': 3,
        'cfc12': 4,
        'cfc113': 7,
        'ch4': 1,
        'co2': 0,
        'hcfc22': 8,
        'hfc125': 9,
        'hfc134a': 10,
        'n2o': 2,
    }
    GHG_HI_NAMELIST_NBR_SPECIES = 11
    OLD_REAL_MISSING_DATA_VALUE = -32768.0

    # Create arrays to populate the namelist.
    namelist_nyears_shape = (GHG_HI_NAMELIST_NBR_SPECIES,)
    namelist_nyears = np.full(namelist_nyears_shape, CMIP7_GHG_HI_NBR_YEARS)
    namelist_years_shape = (GHG_HI_NAMELIST_NBR_SPECIES, CMIP7_GHG_HI_NBR_YEARS)
    namelist_years = np.broadcast_to(
        np.array(range(CMIP7_GHG_HI_BEG_YEAR, CMIP7_GHG_HI_END_YEAR + 1)),
        namelist_years_shape,
    ).T
    namelist_levls = np.zeros(namelist_years.shape)
    for ghg in GHG_HI_NAMELIST_INDEX:
        ghg_index = GHG_HI_NAMELIST_INDEX[ghg]
        namelist_levls[:, ghg_index] = ghg_mmr_dict[ghg]
    namelist_rates = np.full(namelist_years.shape, OLD_REAL_MISSING_DATA_VALUE)

    # Create a dictionary to use to patch the namelist.
    namelist_dict = {
        'clim_fcg_nyears': namelist_nyears,
        'clim_fcg_years': namelist_years,
        'clim_levls': namelist_levls,
        'clim_rates': namelist_rates,
    }

    patch = {'clmchfcg': namelist_dict}
    patch_namelist = f90nml.namelist.Namelist(patch)
    # Set the floating point format to the right value.
    patch_namelist.float_format = '13.6e'
    # The floating point format is ignored unless
    # you print the namelist or convert it to a string.
    patch_str = str(patch_namelist)
    parser = f90nml.Parser()
    patch_str_namelist = parser.reads(patch_str)

    # Create a new namelist by patching the original namelist.
    hi_ghg_namelist_filepath = Path('atmosphere') / 'namelists'
    if not hi_ghg_namelist_filepath.exists():
        raise FileNotFoundError(
            f'Namelist file {hi_ghg_namelist_filepath} does not exist'
        )
    new_namelist_filepath = hi_ghg_namelist_filepath.with_suffix('.nml.patched')
    parser.read(
        hi_ghg_namelist_filepath, patch_str_namelist, new_namelist_filepath
    )

    # Replace the original namelist.
    new_namelist_filepath.replace(hi_ghg_namelist_filepath)


if __name__ == '__main__':
    args = parse_args()

    ghg_mmr_dict = dict()
    for ghg in GHG_MOLAR_MASS:
        ghg_mmr_dict[ghg] = load_cmip7_hi_ghg_mmr(args, ghg)

    # Patch the greenhouse gas variables in the clmchfcg namelist
    cmip7_hi_ghg_patch(ghg_mmr_dict)
