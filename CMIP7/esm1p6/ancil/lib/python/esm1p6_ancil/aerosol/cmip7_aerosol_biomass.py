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
    """Construct the source directory path for CMIP7 biomass burning datasets.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Species name (e.g. 'BC', 'OC', or percentage variable).

    Returns:
        pathlib.Path: Source directory path.
    """
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
    """Construct the file path for a CMIP7 biomass burning netCDF file.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Species or percentage variable name.
        date_range (str): Date range string.

    Returns:
        pathlib.Path: NetCDF file path.
    """
    dirpath = _biomass_dirpath(args, species)
    filename = (
        f"{species}_input4MIPs_emissions_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{date_range}.nc"
    )
    return dirpath / filename


def load_cmip7_aerosol_biomass(args, species, date_range, constraint):
    """Load a biomass burning emission or percentage cube, zero-filling missing
    ocean values.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Species or percentage variable name.
        date_range (str): Date range string.
        constraint (iris.Constraint or None): Loading constraint.

    Returns:
        iris.cube.Cube: Loaded and zero-filled Iris cube.
    """
    cube = load_cmip7_aerosol(
        args, cmip7_aerosol_biomass_filepath, species, date_range, constraint
    )
    # This data is missing over oceans,
    # so needs to be filled with zero for the model
    cube.data = cube.data.filled(0.0)
    return cube


def load_cmip7_aerosol_biomass_list(args, species, date_range_list, constraint):
    """Load, concatenate, and zero-fill biomass burning cubes across multiple
    date range files.

    Args:
        args (argparse.Namespace): Command-line arguments.
        species (str): Species or percentage variable name.
        date_range_list (list of str): List of date range strings.
        constraint (iris.Constraint or None): Loading constraint.

    Returns:
        iris.cube.Cube: Concatenated and zero-filled continuous Iris cube.
    """
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
    """Compute low-level and high-level biomass emission fraction cubes using
    concurrent loading.

    Loads 6 fire emission sources ('AGRI', 'BORF', 'DEFO', 'PEAT', 'SAVA',
    'TEMF') in parallel.
    Partitions into low-level (AGRI, PEAT, SAVA) and high-level (BORF, DEFO,
    TEMF) fractions
    following the UK Met Office CMIP6 methodology.

    Args:
        args (argparse.Namespace): Command-line arguments.
        load_pc_fn (callable): Callback to load percentage cubes.
        species (str): Species name ('BC' or 'OC').

    Returns:
        tuple of (iris.cube.Cube, iris.cube.Cube): (frac_low, frac_high)
            fraction cubes.
    """
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
    """Combine BC and OC biomass emissions into low/high injection heights and
    save ancillary.

    Computes bulk low and high emissions, sets coordinate systems, regrids to
    the model grid,
    zeroes polar rows, attaches STASH item 130 (low) and 131 (high), and writes
    the ancillary file.

    Args:
        args (argparse.Namespace): Command-line arguments.
        load_pc_fn (callable): Callback to load percentage source fractions.
        load_fn (callable): Callback to load total species emissions.
        save_dirpath (pathlib.Path): Destination directory for the ancillary
            file.
    """
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

    save_ancil([low_esm, high_esm], save_dirpath, args.save_filename)

    now = datetime.now()
    print(f"{now}: save_ancil done")
