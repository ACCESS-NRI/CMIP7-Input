import pytest
import iris
from iris.coords import DimCoord
from iris.cube import Cube
from cf_units import Unit
import datetime
import numpy as np

@pytest.fixture
def create_solar_cube_mock():
    def _create_solar_cube_mock(data=None, dim_coords=None, aux_coords=None, yearly_means=None, start_year=1850, output_filepath=None):
        """Build a cube from the given coords, or a monthly time series if no coords are given.

        For the monthly time series, yearly_means sets the mean of each year starting at
        start_year; without it, 1850-1852 is filled with random data.
        """
        if dim_coords is None and aux_coords is None:
            n_years = 3 if yearly_means is None else len(yearly_means)
            years = range(start_year, start_year + n_years)
            time_unit = Unit("days since 1850-01-01", calendar="gregorian")
            points = time_unit.date2num(
                [datetime.datetime(year, month, 15) for year in years for month in range(1, 13)]
            )
            dim_coords = [(DimCoord(points, standard_name="time", units=time_unit), 0)]

            if yearly_means is None:
                data = np.random.rand(n_years * 12)  # Random data for testing
            else:
                # 12 evenly spaced monthly values centred on each yearly mean
                data = np.concatenate([np.linspace(mean - 1.0, mean + 1.0, 12) for mean in yearly_means])

        cube = Cube(
            data,
            dim_coords_and_dims=dim_coords,
            aux_coords_and_dims=aux_coords,
        )

        if output_filepath is not None:
            cube.var_name = "solar_irradiance"
            # a second cube in the same file that should be ignored
            other_cube = Cube([])
            other_cube.var_name = "other_variable"
            #save cube into output_filepath
            iris.save([cube, other_cube], output_filepath)

        return cube
    return _create_solar_cube_mock
