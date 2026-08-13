'''
CMIP7 biomass burning aerosol emissions functions.
Biomass burning aerosol emissions refers to aerosol emissions from the burning of organic matter, such as forests, grasslands, and agricultural residues.

This module provides functions to load and process CMIP7 biomass burning aerosol emissions data,
aggregate the sector dimension by summing all sector contributions into a single field,
and split the biomass burning aerosol emissions fraction into low and high contributions based on the specified species.
'''
import concurrent.futures as cf
from datetime import datetime
from pathlib import Path

import iris
from aerosol.cmip7_aerosol_common import (
    load_cmip7_aerosol,
    load_cmip7_aerosol_list,
    zero_poles,
)
from cmip7_ancil_common import (
    INTERPOLATION_SCHEME,
    esm_grid_mask_cube,
    save_ancil,
    set_coord_system,
)


def _biomass_dirpath(args, species):
    '''
    Return the directory path to the CMIP7 biomass burning aerosol emissions data for the given species.
    '''
    return (
        Path(args.cmip7_source_data_dirname)
        / "CMIP"
        / "DRES"
        / args.dataset_version
        / "atmos"
        / "mon"
        / species
        / "gn"
        / args.dataset_vdate
    )


def cmip7_aerosol_biomass_filepath(args, species, date_range):
    '''
    Return the file path to the CMIP7 biomass burning aerosol emissions data for the given species and date range.   
    '''
    dirpath = _biomass_dirpath(args, species)
    filename = (
        f"{species}_input4MIPs_emissions_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def load_cmip7_aerosol_biomass(args, species, date_range, constraint):
    '''
    Load the CMIP7 biomass burning aerosol emissions data for the given species and date range
    '''
    cube = load_cmip7_aerosol(
        args, cmip7_aerosol_biomass_filepath, species, date_range, constraint
    )
    # This data is missing over oceans,
    # so needs to be filled with zero for the model
    cube.data = cube.data.filled(0.0)
    return cube


def load_cmip7_aerosol_biomass_list(args, species, date_range_list, constraint):
    '''
    Load the CMIP7 biomass burning aerosol emissions data for the given species and list of date ranges, and apply the given constraint.
    '''
    cube = load_cmip7_aerosol_list(
        args,
        cmip7_aerosol_biomass_filepath,
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
    '''
    Split the biomass burning aerosol emissions fraction into low and high contributions based on the specified species.
    '''

    # Sources for the low and high contributions of biomass burning aerosol emissions. 
    # low: AGRI, PEAT, SAVA
    # high: BORF, DEFO, TEMF
    sources = ["AGRI", "BORF", "DEFO", "PEAT", "SAVA", "TEMF"]
    pc = dict()
    futures = dict()
    max_workers = len(sources)
    # Use a process pool executor to load the biomass burning aerosol emissions fraction for each source in parallel.
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

    # If force_load is True, force the realization of the data for both low and high contributions to ensure that the data is loaded into memory. 
    # This is useful for debugging and performance monitoring, as it allows you to see when the data has been fully loaded and processed.
    if force_load:
        _ = frac_low.data
        now = datetime.now()
        print(f"{now}: Realised bb {species} low")
        _ = frac_high.data
        now = datetime.now()
        print(f"{now}: Realised bb {species} high")

    # Return the low and high contributions of the biomass burning aerosol emissions fraction for the specified species.
    return frac_low, frac_high


def save_cmip7_aerosol_biomass(args, load_pc_fn, load_fn, save_dirpath):
    """Create and save low- and high-level biomass-burning aerosol fields.

    The CMIP7 biomass-burning emissions are supplied separately for black
    carbon (BC) and organic carbon (OC).  This function combines each species
    with source fractions from :func:`split_frac_low_high` to create two
    fields: one for low-level emissions and one for high-level emissions.
    Both fields are then regridded to the ESM1.5 grid, corrected at the poles,
    assigned their UM STASH identifiers, and written as an ancillary file.

    Parameters
    ----------
    args
        Parsed command-line arguments used by the loader and grid-mask
        functions.
    load_pc_fn
        Callable that loads the percentage contribution for a biomass-burning
        source.
    load_fn
        Callable that loads the total biomass-burning field for BC or OC.
    save_dirpath
        Directory in which the generated ancillary file is saved.

    Notes
    -----
    The low-level field is saved with STASH item 130 and the high-level field
    with STASH item 131.  Missing source data are filled with zero by the
    biomass-loading functions before the fields are combined.
    """
    # Calculate the low- and high-level source fractions for each aerosol
    # species.  The fractions are returned as decimal values.
    bc_frac_low, bc_frac_high = split_frac_low_high(args, load_pc_fn, "BC")
    oc_frac_low, oc_frac_high = split_frac_low_high(args, load_pc_fn, "OC")

    # Load the total biomass-burning emissions for black carbon and organic
    # carbon.
    bc = load_fn(args, "BC")
    oc = load_fn(args, "OC")

    # Apply the source fractions and combine the BC and OC contributions into
    # separate low- and high-level aerosol fields.
    low = bc * bc_frac_low + oc * oc_frac_low
    high = bc * bc_frac_high + oc * oc_frac_high

    # Force lazy calculations to finish before continuing when requested.
    if force_load:
        _ = low.data
        _ = high.data
        now = datetime.now()
        print(f"{now}: LO, HI done")

    # Regridding requires the source coordinates to have compatible coordinate
    # system metadata.
    set_coord_system(low)
    set_coord_system(high)

    now = datetime.now()
    print(f"{now}: set_coord_system done")

    # Regrid both fields onto the ESM1.5 grid.
    esm_grid_mask = esm_grid_mask_cube(args)
    low_esm = low.regrid(esm_grid_mask, INTERPOLATION_SCHEME)
    high_esm = high.regrid(esm_grid_mask, INTERPOLATION_SCHEME)

    now = datetime.now()
    print(f"{now}: regrid done")

    # Set polar values to zero.
    zero_poles(low_esm)
    zero_poles(high_esm)

    now = datetime.now()
    print(f"{now}: zero_poles done")

    # Attach the STASH identifiers expected by the UM ancillary-file format.
    low_esm.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=130
    )
    high_esm.attributes["STASH"] = iris.fileformats.pp.STASH(
        model=1, section=0, item=131
    )

    # Save both fields in the same ancillary file.
    save_ancil([low_esm, high_esm], save_dirpath, args.save_filename)

    now = datetime.now()
    print(f"{now}: save_ancil done")
