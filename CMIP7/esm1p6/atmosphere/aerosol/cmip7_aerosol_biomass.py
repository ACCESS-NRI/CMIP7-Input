import concurrent.futures as cf
import os
from datetime import datetime

import iris
from aerosol.cmip7_aerosol_common import (
    load_cmip7_aerosol,
    load_cmip7_aerosol_list,
    zero_poles,
)
from cmip7_ancil_common import (
    INTERPOLATION_SCHEME,
    esm_grid_mask_cube,
    extend_years,
    save_ancil,
    set_coord_system,
)
from cmip7_ancil_path_classes import Cmip7Filepath

cmip7_aerosol_biomass_dirname_template = os.path.join(
    "DRES", "{version}", "atmos", "{period}", "{species}", "gn", "{vdate}"
)
cmip7_aerosol_biomass_filename_template = (
    "{species}_input4MIPs_emissions_CMIP_{version}_gn_{date_range}.nc"
)


def cmip7_aerosol_biomass_filepath(args, species, date_range):
    filepath = Cmip7Filepath(
        root_dirname=args.cmip7_source_data_dirname,
        dirname_template=cmip7_aerosol_biomass_dirname_template,
        filename_template=cmip7_aerosol_biomass_filename_template,
        version=args.dataset_version,
        vdate=args.dataset_vdate,
        period="mon",
        date_range=date_range,
        species=species,
    )
    return filepath()


def cmip7_aerosol_biomass_filepath_list(args, species, date_range_list):
    return [
        cmip7_aerosol_biomass_filepath(args, species, date_range)
        for date_range in date_range_list
    ]


def load_cmip7_aerosol_biomass(args, species, date_range, constraint):
    cube = load_cmip7_aerosol(
        args, cmip7_aerosol_biomass_filepath, species, date_range, constraint
    )
    # This data is missing over oceans,
    # so needs to be filled with zero for the model
    cube.data = cube.data.filled(0.0)
    return cube


def load_cmip7_aerosol_biomass_list(args, species, date_range_list, constraint):
    cube = load_cmip7_aerosol_list(
        args,
        cmip7_aerosol_biomass_filepath_list,
        species,
        date_range_list,
        constraint,
    )
    # This data is missing over oceans,
    # so needs to be filled with zero for the model
    cube.data = cube.data.filled(0.0)
    return cube


force_load = True


def split_frac_low_high(args, load_pc_fn, species):
    sources = ["AGRI", "BORF", "DEFO", "PEAT", "SAVA", "TEMF"]
    pc = dict()
    futures = dict()
    max_workers = len(sources)
    with cf.ProcessPoolExecutor(max_workers=max_workers) as ex:
        for source in sources:
            futures[source] = ex.submit(
                load_pc_fn, args, f"{species}percentage{source}"
            )
        for source in sources:
            pc[source] = futures[source].result()
    # For the low/high split follow Met Office CMIP6
    # low: AGRI, PEAT, SAVA
    # high: BORF, DEFO, TEMF
    frac_low = 0.01 * (pc["AGRI"] + pc["PEAT"] + pc["SAVA"])
    frac_high = 0.01 * (pc["BORF"] + pc["DEFO"] + pc["TEMF"])
    if force_load:
        _ = frac_low.data
        now = datetime.now()
        print(f"{now}: Realised bb {species} low")
        _ = frac_high.data
        now = datetime.now()
        print(f"{now}: Realised bb {species} high")
    return frac_low, frac_high


def save_cmip7_aerosol_biomass(args, load_pc_fn, load_fn, save_dirpath):
    bc_frac_low, bc_frac_high = split_frac_low_high(args, load_pc_fn, "BC")
    oc_frac_low, oc_frac_high = split_frac_low_high(args, load_pc_fn, "OC")

    bc = load_fn(args, "BC")
    oc = load_fn(args, "OC")

    low = bc * bc_frac_low + oc * oc_frac_low
    high = bc * bc_frac_high + oc * oc_frac_high

    if force_load:
        _ = low.data
        _ = high.data
        now = datetime.now()
        print(f"{now}: LO, HI done")

    # Regrid requires matching coordinate systems
    set_coord_system(low)
    set_coord_system(high)

    now = datetime.now()
    print(f"{now}: set_coord_system done")

    esm_grid_mask = esm_grid_mask_cube(args)
    low_esm = low.regrid(esm_grid_mask, INTERPOLATION_SCHEME)
    high_esm = high.regrid(esm_grid_mask, INTERPOLATION_SCHEME)

    now = datetime.now()
    print(f"{now}: regrid done")

    zero_poles(low_esm)
    zero_poles(high_esm)

    now = datetime.now()
    print(f"{now}: zero_poles done")

    low_esm.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=130
    )
    high_esm.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=131
    )

    # Extend the historical time series, if any,
    # by duplicating the first and last years
    low_esm = extend_years(low_esm)
    high_esm = extend_years(high_esm)

    save_ancil([low_esm, high_esm], save_dirpath, args.save_filename)

    now = datetime.now()
    print(f"{now}: save_ancil done")
