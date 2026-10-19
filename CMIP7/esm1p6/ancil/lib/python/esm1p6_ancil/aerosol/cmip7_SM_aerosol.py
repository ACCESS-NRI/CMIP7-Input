from pathlib import Path

import iris
from aerosol.cmip7_aerosol_common import load_cmip7_aerosol
from cmip7_ancil_common import cmip7_date_constraint_from_years
from cmip7_ancil_constants import ANCIL_TODAY
from cmip7_SM import CMIP7_SM_BEG_YEAR, CMIP7_SM_END_YEAR, CMIP7_SM_EXT_END_YEAR
from dataset import DatasetConfig
from iris.util import equalise_attributes, unify_time_units


def sm_configs(args, aircraft=False):
    """Load the ScenarioMIP emissions dataset configurations.

    Args:
        args (argparse.Namespace): Command-line arguments with the config
            file, scenario, and extension options.
        aircraft (bool, optional): Whether to load the aircraft emissions
            configurations (sections '<scenario>-air' and
            '<scenario>-air-ext') instead of the surface emissions
            configurations (sections '<scenario>' and '<scenario>-ext').
            Defaults to False.

    Returns:
        tuple of (dataset.DatasetConfig, dataset.DatasetConfig or None):
            The base configuration, and the extension configuration if
            ``args.ext`` is set (otherwise None).
    """
    section = f"{args.scenario}-air" if aircraft else args.scenario
    config = DatasetConfig.from_yaml(args.config, section=section)
    ext_config = (
        DatasetConfig.from_yaml(args.config, section=f"{section}-ext")
        if args.ext
        else None
    )
    return config, ext_config


def sm_target_end_year(args):
    """Return the final year of the ScenarioMIP time series.

    Args:
        args (argparse.Namespace): Command-line arguments with ``ext`` and
            ``end_year`` options.

    Returns:
        int: ``end_year`` (default CMIP7_SM_EXT_END_YEAR) if extending the
            series beyond 2100, otherwise CMIP7_SM_END_YEAR.
    """
    if args.ext:
        return args.end_year or CMIP7_SM_EXT_END_YEAR
    return CMIP7_SM_END_YEAR


def load_cmip7_sm_aerosol_series(
    args, config, ext_config, variable_id, fill_masked=False
):
    """Load a ScenarioMIP emissions series, optionally extended beyond 2100.

    Args:
        args (argparse.Namespace): Command-line arguments.
        config (dataset.DatasetConfig): Configuration of the base
            dataset (2022-2100).
        ext_config (dataset.DatasetConfig or None): Configuration of the
            extension dataset, or None for no extension.
        variable_id (str): DRS variable identifier.
        fill_masked (bool, optional): Whether to fill masked values with
            zero before concatenating. Defaults to False.

    Returns:
        iris.cube.Cube: Base cube, concatenated with the extension cube
            if ``ext_config`` is not None.
    """
    base_cube = load_cmip7_aerosol(
        config.to_dataset(variable_id=variable_id),
        cmip7_date_constraint_from_years(CMIP7_SM_BEG_YEAR, CMIP7_SM_END_YEAR),
    )
    if ext_config is None:
        if fill_masked:
            base_cube.data = base_cube.data.filled(0.0)
        return base_cube

    ext_cube = load_cmip7_aerosol(
        ext_config.to_dataset(variable_id=variable_id),
        cmip7_date_constraint_from_years(
            CMIP7_SM_END_YEAR + 1, sm_target_end_year(args)
        ),
    )
    if fill_masked:
        base_cube.data = base_cube.data.filled(0.0)
        ext_cube.data = ext_cube.data.filled(0.0)
    cubelist = iris.cube.CubeList([base_cube, ext_cube])
    equalise_attributes(cubelist)
    unify_time_units(cubelist)
    return cubelist.concatenate_cube()


def esm_sm_aerosol_ancil_dirpath(args):
    """Construct the base directory path for ScenarioMIP aerosol ancillaries.

    Args:
        args (argparse.Namespace): Command-line arguments containing
            ancil_target_dirname and scenario.

    Returns:
        pathlib.Path: Directory path under
            modern/scen7-{scenario}/atmosphere/aerosol.
    """
    return (
        Path(args.ancil_target_dirname)
        / "modern"
        / f"scen7-{args.scenario}"
        / "atmosphere"
        / "aerosol"
    )


def esm_sm_aerosol_save_dirpath(args):
    """Construct the target directory path for saving ScenarioMIP aerosol
    ancillary files.

    Args:
        args (argparse.Namespace): Command-line arguments containing output
            path configuration (ancil_target_dirname, scenario,
            esm_grid_rel_dirname).

    Returns:
        pathlib.Path: Target directory path with resolution and date stamps.
    """
    return (
        esm_sm_aerosol_ancil_dirpath(args)
        / args.esm_grid_rel_dirname
        / ANCIL_TODAY
    )
