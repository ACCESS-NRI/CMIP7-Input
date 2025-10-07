from argparse import ArgumentParser

import cftime
import iris
import numpy as np
from cmip7_ancil_argparse import dataset_parser, path_parser
from cmip7_HI import (
    CMIP7_HI_BEG_YEAR,
    CMIP7_HI_END_YEAR,
    esm_hi_forcing_save_dirpath,
)
from volcanic.cmip7_volcanic import (
    SAOD_WAVELENGTH,
    cmip7_volcanic_dirpath,
    constrain_to_wavelength,
    mean_over_latitudes,
    sum_over_height_layers,
)

CMIP7_HI_VOLCANIC_BEG_YEAR = 1850
CMIP7_HI_VOLCANIC_END_YEAR = 2023
CMIP7_HI_SAOD_ARRAY_END_YEAR = 2300
MONTHS_IN_YEAR = 12
NBR_OF_BANDS = 4


def parse_args():
    parser = ArgumentParser(
        prog="cmip7_HI_volcanic_generate",
        description=(
            "Generate input files from CMIP7 historical volcanic forcings"
        ),
        parents=[path_parser(), dataset_parser()],
    )
    parser.add_argument("--dataset-date-range")
    parser.add_argument("--save-filename")
    return parser.parse_args()


def cmip7_hi_volcanic_filename(args):
    return (
        f"ext_input4MIPs_aerosolProperties_CMIP_"
        f"{args.dataset_version}_gnz_"
        f"{args.dataset_date_range}.nc"
    )


def constrain_to_year_month(cube, year, month):
    """
    Constrain to a given year and month.
    """
    calendar = "proleptic_gregorian"
    beg_date = cftime.datetime(year, month, 1, calendar=calendar)
    end_year = year + 1 if month == MONTHS_IN_YEAR else year
    end_month = 1 if month == MONTHS_IN_YEAR else month + 1
    end_date = cftime.datetime(end_year, end_month, 1, calendar=calendar)
    ym_constraint = iris.Constraint(
        time=lambda cell: beg_date <= cell < end_date
    )
    return cube.extract(ym_constraint)


def constrain_to_latitude_band(cube, band):
    """
    Constrain to one of four equal latitude bands.
    """
    lat_bound = [-90, -30, 0, 30, 90]
    lat_constraint = iris.Constraint(
        latitude=lambda cell: lat_bound[band] <= cell < lat_bound[band + 1]
    )
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
    # Keep the BEG_YEAR SAOD values in an array.
    saod_for_beg_year = np.zeros((MONTHS_IN_YEAR, NBR_OF_BANDS))
    with open(save_filepath, "w") as save_file:
        # Iterate over years and months.
        for year in range(
            CMIP7_HI_VOLCANIC_BEG_YEAR, CMIP7_HI_VOLCANIC_END_YEAR + 1
        ):
            for month in range(1, MONTHS_IN_YEAR + 1):
                print(f"{year:4d} {month:4d}", end="", file=save_file)
                ym_cube = constrain_to_year_month(cube, year, month)

                # Divide into latitude bands.
                for lat_band_nbr in range(NBR_OF_BANDS):
                    lat_cube = constrain_to_latitude_band(ym_cube, lat_band_nbr)

                    # Find the mean over all latitudes included in this band,
                    # weighted by area.
                    lat_cube = mean_over_latitudes(lat_cube)

                    # Calculate the stratospheric aerosol optical depth
                    # by summing over stratospheric layers,
                    # weighted by layer height.
                    lat_cube = sum_over_height_layers(lat_cube)
                    saod = lat_cube.data * 10000.0
                    print(
                        f"{int(saod):5d}",
                        end="",
                        file=save_file,
                    )
                    # Save the SAOD values for CMIP7_HI_VOLCANIC_BEG_YEAR.
                    if year == CMIP7_HI_VOLCANIC_BEG_YEAR:
                        saod_for_beg_year[month - 1, lat_band_nbr] = saod
                print(file=save_file)
        # For years from CMIP7_HI_VOLCANIC_END_YEAR + 1 to
        # CMIP7_HI_SAOD_ARRAY_END_YEAR use the saved SAOD values in
        # saod_for_beg_year.
        for year in range(
            CMIP7_HI_VOLCANIC_END_YEAR + 1, CMIP7_HI_SAOD_ARRAY_END_YEAR + 1
        ):
            for month in range(1, MONTHS_IN_YEAR + 1):
                print(f"{year:4d} {month:4d}", end="", file=save_file)

                # Divide into latitude bands.
                for lat_band_nbr in range(NBR_OF_BANDS):
                    saod = saod_for_beg_year[month - 1, lat_band_nbr]
                    print(
                        f"{int(saod):5d}",
                        end="",
                        file=save_file,
                    )
                print(file=save_file)


if __name__ == "__main__":
    args = parse_args()

    dataset_path = cmip7_volcanic_dirpath(
        args, period="mon"
    ) / cmip7_hi_volcanic_filename(args)

    # Calculate and save the average stratospheric aerosol optical depth.
    save_hi_stratospheric_aerosol_optical_depth(args, dataset_path)
