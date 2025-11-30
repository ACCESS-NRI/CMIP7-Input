from argparse import ArgumentParser
from pathlib import Path

import f90nml
import iris
import numpy as np
from cmip7_ancil_argparse import dataset_parser, path_parser
from cmip7_HI import (
    CMIP7_HI_BEG_YEAR,
    CMIP7_HI_END_YEAR,
    CMIP7_HI_NBR_YEARS,
)
from ghg.cmip7_ghg import (
    GHG_MOLAR_MASS,
    cmip7_ghg_dirpath,
    cmip7_ghg_filename,
    cmip7_ghg_mmr,
    cmip7_pro_greg_date_constraint_from_years,
)


def parse_args():
    parser = ArgumentParser(
        parents=[path_parser(), dataset_parser()],
        prog="cmip7_HI_ghg_generate",
        description=(
            "Generate input files from CMIP7 historical greenhouse gas forcings"
        ),
    )
    parser.add_argument("--dataset-date-range")
    return parser.parse_args()


def load_cmip7_hi_ghg_mmr(args, ghg):
    cmip7_filepath = cmip7_ghg_dirpath(args, ghg) / cmip7_ghg_filename(
        args, ghg
    )

    # Read in the CMIP7 cube.
    full_cube = iris.load_cube(cmip7_filepath)

    # Check that we have the right greenhouse gas.
    variable_id = full_cube.metadata.attributes["variable_id"]
    assert ghg == variable_id

    # Extract the historical years.
    date_constraint = cmip7_pro_greg_date_constraint_from_years(
        CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR
    )
    hi_cube = full_cube.extract(date_constraint)

    # Determine the mass mixing ratio.
    ghg_mmr_list = []
    for year in range(CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR + 1):
        year_constraint = cmip7_pro_greg_date_constraint_from_years(year, year)
        year_cube = hi_cube.extract(year_constraint)
        ghg_mmr_list.append(cmip7_ghg_mmr(year_cube, ghg))
    return ghg_mmr_list


def read_namelists_lines_up_to(namelists_filepath, exclude_str):
    """
    Read lines from namelists_filepath up to but not including
    the line containing exclude_str.
    """
    if not namelists_filepath.exists():
        raise FileNotFoundError(
            f"Namelist file {namelists_filepath} does not exist"
        )
    # Read the atmosphere/namelists file up to but not including
    # the clmchfcg namelist.
    namelists_str = ""
    with open(namelists_filepath, "r") as namelists_file:
        namelists_line = namelists_file.readline()
        while namelists_line and (
           "&" + exclude_str not in namelists_line.lower()
        ):
           namelists_str += namelists_line
           namelists_line = namelists_file.readline()
    return namelists_str


def format_namelist(
        namelist,
        float_format="13.6e",
        end_comma=True,
        false_repr=".FALSE.",
        true_repr=".TRUE.",
        uppercase=True
    ):
    """
    Change the namelist formatting to the preferred format.
    """
    namelist.float_format = float_format
    namelist.end_comma = end_comma
    namelist.false_repr = false_repr
    namelist.true_repr = true_repr
    namelist.uppercase = uppercase


def cmip7_hi_ghg_namelist_str(ghg_mmr_dict, ghg_namelist_name):
    """
    Use the greenhouse gas mass mixing ratios to
    produce a replacement clmchfcg namelist as a string.
    """
    # Map each greenhouse gas to an index in the
    # historical climate forcing arrays.
    GHG_HI_NAMELIST_INDEX = {
        "cfc11": 3,
        "cfc12": 4,
        "cfc113": 7,
        "ch4": 1,
        "co2": 0,
        "hcfc22": 8,
        "hfc125": 9,
        "hfc134a": 10,
        "n2o": 2,
    }
    GHG_HI_NAMELIST_NBR_SPECIES = 11
    OLD_REAL_MISSING_DATA_VALUE = -32768.0

    # Create arrays to populate the namelist.
    namelist_nyears_shape = (GHG_HI_NAMELIST_NBR_SPECIES,)
    namelist_nyears = np.full(namelist_nyears_shape, CMIP7_HI_NBR_YEARS)
    namelist_years_shape = (GHG_HI_NAMELIST_NBR_SPECIES, CMIP7_HI_NBR_YEARS)
    namelist_years = np.broadcast_to(
        np.array(range(CMIP7_HI_BEG_YEAR, CMIP7_HI_END_YEAR + 1)),
        namelist_years_shape,
    ).T
    namelist_levls = np.zeros(namelist_years.shape)
    for ghg in GHG_HI_NAMELIST_INDEX:
        ghg_index = GHG_HI_NAMELIST_INDEX[ghg]
        namelist_levls[:, ghg_index] = ghg_mmr_dict[ghg]
    namelist_rates = np.full(namelist_years.shape, OLD_REAL_MISSING_DATA_VALUE)

    # Create a dictionary to use to patch the namelist.
    namelist_dict = {
        "l_clmchfcg": True,
        "clim_fcg_nyears": namelist_nyears,
        "clim_fcg_years": namelist_years,
        "clim_levls": namelist_levls,
        "clim_rates": namelist_rates,
    }

    patch = {ghg_namelist_name: namelist_dict}
    patch_namelist = f90nml.namelist.Namelist(patch)

    # Change the namelist arrays to row major.
    patch_str = str(patch_namelist)
    parser = f90nml.Parser()
    parser.row_major = True
    row_major_patch_namelist = parser.reads(patch_str)
    # Correctly format the namelist.
    format_namelist(row_major_patch_namelist)
    # The format is ignored unless you print the namelist or
    # convert it to a string.
    return str(row_major_patch_namelist)


def update_namelists_file(ghg_mmr_dict):
    """
    Use the greenhouse gas mass mixing ratios in ghg_mmr_dict
    to replace the greenhouse gas namelist in the relevant namelists file.
    """
    namelists_filepath = Path("atmosphere") / "namelists"
    ghg_namelist_name = "clmchfcg"
    # Read the original namelists file up to ghg_namelist_name.
    namelists_str = read_namelists_lines_up_to(
        namelists_filepath,
        ghg_namelist_name)
    # Use ghg_mmr_dict and ghg_namelist_name to create
    # a replacement namelist as a string.
    ghg_namelist_str = cmip7_hi_ghg_namelist_str(
        ghg_mmr_dict,
        ghg_namelist_name)
    # Replace the original namelists file.
    with open(namelists_filepath, "w") as namelists_file:
        print(namelists_str + ghg_namelist_str, file=namelists_file)


if __name__ == "__main__":
    args = parse_args()

    ghg_mmr_dict = dict()
    for ghg in GHG_MOLAR_MASS:
        ghg_mmr_dict[ghg] = load_cmip7_hi_ghg_mmr(args, ghg)

    # Patch the greenhouse gas variables in the clmchfcg namelist
    cmip7_hi_ghg_patch(ghg_mmr_dict)
