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
    extend_years,
    save_ancil,
)
from cmip7_ancil_constants import ANCIL_TODAY

SPECIES = "CO2"
STASH_ITEM = 251


def esm_eh_co2_save_dirpath(args):
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
    cube = load_cmip7_hi_aerosol_anthro(args, SPECIES)
    cube_sum = cube.collapsed(["sector"], iris.analysis.SUM)
    cube_air = load_cmip7_hi_aerosol_air_anthro(args, SPECIES)
    cube_air_sum = cube_air.collapsed(["altitude"], iris.analysis.SUM)
    cube_tot = cube_sum + cube_air_sum

    esm_cube = cube_tot.regrid(esm_grid_mask_cube(args), INTERPOLATION_SCHEME)
    esm_cube.data = esm_cube.data.filled(0.0)
    zero_poles(esm_cube)
    esm_cube.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=STASH_ITEM
    )
    # Extend the historical time series, if any,
    # by duplicating the first and last years
    esm_cube = extend_years(esm_cube)

    save_dirpath = esm_eh_co2_save_dirpath(args)
    save_ancil(esm_cube, save_dirpath, args.save_filename)


if __name__ == "__main__":
    args = parse_args(species=SPECIES)

    cmip7_eh_co2_anthro_interpolate(args)
