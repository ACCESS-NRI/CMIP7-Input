from pathlib import Path

import iris
import numpy as np


# The prescribed wavelength for stratospheric aerosol optical depth
SAOD_WAVELENGTH = 550.0 * 1e-9


def cmip7_volcanic_dirpath(args, period):
    return (
        Path(args.cmip7_source_data_dirname)
        / 'uoexeter'
        / args.dataset_version
        / 'atmos'
        / period
        / 'ext'
        / 'gnz'
        / args.dataset_vdate)


def constrain_to_wavelength(cube, wavelength):
    """ 
    Constrain to just the prescribed wavelength.
    """
    wl_constraint = iris.Constraint(radiation_wavelength=wavelength)
    return cube.extract(wl_constraint)


def mean_over_latitudes(cube):
    """
    Find the mean over all latitude bands, weighted by area.
    """
    lat_weights = iris.analysis.cartography.cosine_latitude_weights(cube)
    return cube.collapsed(
        ["latitude"],
        iris.analysis.MEAN,
        weights=lat_weights)


def sum_over_height_layers(cube):
    """
    Calculate the stratospheric aerosol optical depth by
    summing over stratospheric layers, weighted by layer height.
    """
    height_coord = next(
        c for c in cube.coords() 
        if c.standard_name == "height_above_mean_sea_level")
    height_weights = np.diff(height_coord.bounds).flatten()
    return cube.collapsed(
        ["height_above_mean_sea_level"],
        iris.analysis.SUM,
        weights=height_weights)
