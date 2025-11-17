# Interpolate CMIP7 PI SO2 emissions to ESM1-6 grid

import tempfile
from os import fsdecode
from pathlib import Path

import iris
import netCDF4
import numpy as np
from esm1p6_ancil.aerosol.cmip7_aerosol_anthro import (
    cmip7_aerosol_anthro_filepath,
)
from esm1p6_ancil.aerosol.cmip7_aerosol_common import zero_poles
from esm1p6_ancil.cmip7_ancil_common import (
    INTERPOLATION_SCHEME,
    esm_grid_mask_cube,
    save_ancil,
)

DMS_NAME_CONSTRAINT = iris.Constraint(
    name="tendency_of_atmosphere_mass_content_of_"
    "dimethyl_sulfide_expressed_as_sulfur_due_to_emission"
)


def load_sector_dict(args, date_range_maybe_list):
    date_range = (
        date_range_maybe_list[0]
        if isinstance(date_range_maybe_list, list)
        else date_range_maybe_list
    )
    # Iris doesn't read the sector coordinate so use netCDF4
    d = netCDF4.Dataset(cmip7_aerosol_anthro_filepath(args, "SO2", date_range))
    sectord = dict()
    for s in d["sector"].ids.split(";"):
        i, name = s.split(":")
        sectord[name.strip()] = int(i)
    d.close()
    return sectord


def load_dms(args, dms_ancil_dirpath, fix_ancil_date_fn):
    # Use the CMIP6 DMS
    dms_ancil_pathname = fsdecode(dms_ancil_dirpath / args.dms_ancil_filename)
    with tempfile.TemporaryDirectory() as temp:
        dms_ancil_tempname = fsdecode(Path(temp) / args.dms_ancil_filename)
        # Create a temporary file with fixed dates
        # from the CMIP6 DMS file
        fix_ancil_date_fn(ifile=dms_ancil_pathname, ofile=dms_ancil_tempname)
        dms = iris.load_cube(dms_ancil_tempname, DMS_NAME_CONSTRAINT)
        # Force load since temp is temporary
        _ = dms.data
        return dms


def tile_yearly_data(from_cube, to_cube):
    from_mons = from_cube.data.shape[0]
    from_years = from_mons // 12
    to_year0 = to_cube.data[0:12, :, :]
    return np.tile(to_year0, (from_years, 1, 1))


def save_cmip7_so2_aerosol_anthro(
    args, cmip7_load_fn, date_range, dms_load_fn, save_dirpath
):
    cmip7_so2 = cmip7_load_fn(args, "SO2")

    # Iris doesn't read the sector coordinate
    sectord = load_sector_dict(args, date_range)

    cmip7_so2_high = (
        cmip7_so2[:, sectord["Energy"]]
        + 0.5 * cmip7_so2[:, sectord["Industrial"]]
    )
    cmip7_so2_tot = cmip7_so2.collapsed(["sector"], iris.analysis.SUM)
    cmip7_so2_low = cmip7_so2_tot - cmip7_so2_high

    # For ESM1.6, factor of 0.5 to go to mass of S
    so2_low = 0.5 * cmip7_so2_low.regrid(
        esm_grid_mask_cube(args), INTERPOLATION_SCHEME
    )
    so2_high = 0.5 * cmip7_so2_high.regrid(
        esm_grid_mask_cube(args), INTERPOLATION_SCHEME
    )

    so2_low.data = so2_low.data.filled(0.0)
    so2_high.data = so2_high.data.filled(0.0)

    zero_poles(so2_low)
    zero_poles(so2_high)

    so2_low.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=58
    )
    so2_high.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=126
    )

    # Need to remove the sector coordinate before saving
    # because high doesn't have it
    so2_low.remove_coord("sector")
    # Use the CMIP6 DMS
    cmip6_dms = dms_load_fn(args)

    # Extend the yearly dms data
    dms_data = tile_yearly_data(so2_low, cmip6_dms)
    dms_time = so2_low.coord("time")
    dms_lat = cmip6_dms.coord("latitude")
    dms_lon = cmip6_dms.coord("longitude")
    dms = iris.cube.Cube(
        dms_data,
        standard_name=cmip6_dms.standard_name,
        long_name=cmip6_dms.long_name,
        var_name=cmip6_dms.var_name,
        units=cmip6_dms.units,
        attributes=cmip6_dms.attributes,
        cell_methods=cmip6_dms.cell_methods,
        dim_coords_and_dims=[
            (dms_time, 0),
            (dms_lat, 1),
            (dms_lon, 2),
        ],
    )

    save_ancil([so2_low, so2_high, dms], save_dirpath, args.save_filename)
