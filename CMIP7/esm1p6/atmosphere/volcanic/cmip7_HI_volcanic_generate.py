
from cmip7_ancil_argparse import (
        dataset_parser,
        path_parser)
from cmip7_HI import esm_hi_forcing_save_dirpath
from volcanic.cmip7_volcanic import (
        SAOD_WAVELENGTH,
        cmip7_volcanic_dirpath,
        constrain_to_wavelength,
        mean_over_latitudes,
        sum_over_height_layers)

from argparse import ArgumentParser
from pathlib import Path

import cftime
import f90nml
import iris
import numpy as np


CMIP7_HI_VOLCANIC_BEG_YEAR = 1850
CMIP7_HI_VOLCANIC_END_YEAR = 2023


def parse_args():
    parser = ArgumentParser(
            prog='cmip7_HI_volcanic_generate',
            description=(
                'Generate input files from CMIP7 historical volcanic forcings'),
            parents=[
                path_parser(),
                dataset_parser()])
    parser.add_argument('--dataset-date-range')
    parser.add_argument('--save-filename')
    return parser.parse_args()


def cmip7_hi_volcanic_filename(args):

    return (f'ext_input4MIPs_aerosolProperties_CMIP_'
            f'{args.dataset_version}_gnz_'
            f'{args.dataset_date_range}.nc')


def constrain_to_year_month(cube, year, month):
    """
    Constrain to a given year and month.
    """
    calendar = 'proleptic_gregorian'
    beg_date = cftime.datetime(year, month, 1, calendar=calendar)
    end_year = year + 1 if month == 12 else year
    end_month = 1 if month == 12 else month + 1
    end_date = cftime.datetime(end_year, end_month, 1, calendar=calendar)
    ym_constraint_fn = lambda cell: beg_date <= cell < end_date
    ym_constraint =  iris.Constraint(time=ym_constraint_fn)
    return cube.extract(ym_constraint)


def constrain_to_latitude_band(cube, band_nbr):
    """
    Constrain to one of four equal latitude bands.
    """
    lat_band_bound = [-90, -30, 0, 30, 90]
    lat_constraint_fn = lambda cell: (
        lat_band_bound[band_nbr] <= cell < lat_band_bound[band_nbr + 1])
    lat_constraint = iris.Constraint(latitude=lat_constraint_fn)
    return cube.extract(lat_constraint)


def save_hi_stratospheric_aerosol_optical_depth(args, dataset_path):
    """
    Calculate the average stratospheric aerosol optical depth (SAOD)
    for each historical month by averaging extinction over latitude,
    and summing over stratospheric layers. Save to the save file.
    """
    # Load the dataset into an Iris cube.
    cube = iris.load_cube(dataset_path)
    
    # Constrain to just the CMIP7 prescribed wavelength.
    cube = constrain_to_wavelength(cube, SAOD_WAVELENGTH)
    
    # Replace NaN values with 0.
    np.nan_to_num(cube.data, copy=False)

    save_dirpath = esm_hi_forcing_save_dirpath(args)
    # Ensure that the save directory exists.
    save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
    save_filepath = save_dirpath / args.save_filename
    with open(save_filepath, 'w') as save_file:
        # Iterate over years and months.
        for year in range(
                CMIP7_HI_VOLCANIC_BEG_YEAR,
                CMIP7_HI_VOLCANIC_END_YEAR + 1):
            for month in range(1, 13):
                print(
                    f'{year:4d} {month:4d}',
                    end='',
                    file=save_file)
                ym_cube = constrain_to_year_month(cube, year, month)
                
                # Divide into 4 latitude bands.
                for lat_band_nbr in range(4):
                    lat_cube = constrain_to_latitude_band(ym_cube, lat_band_nbr)
                    
                    # Find the mean over all latitudes included in this band,
                    # weighted by area.
                    lat_cube = mean_over_latitudes(lat_cube)
                    
                    # Calculate the stratospheric aerosol optical depth by
                    # summing over stratospheric layers, weighted by layer height.
                    lat_cube = sum_over_height_layers(lat_cube)
                    print(
                        f'{int(lat_cube.data * 10000.0):5d}',
                        end='',
                        file=save_file)
                print(file=save_file)


if __name__ == '__main__':

    args = parse_args()

    dataset_path = (
            cmip7_volcanic_dirpath(args, period='mon') 
            / cmip7_hi_volcanic_filename(args))

    # Calculate and save the average stratospheric aerosol optical depth.
    save_hi_stratospheric_aerosol_optical_depth(args, dataset_path)
