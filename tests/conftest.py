"""Shared pytest fixtures for constructing Iris cubes."""

import datetime

import numpy as np
import pytest
from cf_units import Unit
from iris.coords import AuxCoord, DimCoord
from iris.cube import Cube


@pytest.fixture
def make_cube():
    """Build a cube from data and Iris coordinate/dimension pairs."""

    def _make_cube(
        data,
        *,
        dim_coords_and_dims=None,
        aux_coords_and_dims=None,
        **metadata,
    ):
        return Cube(
            data,
            dim_coords_and_dims=dim_coords_and_dims,
            aux_coords_and_dims=aux_coords_and_dims,
            **metadata,
        )

    return _make_cube


@pytest.fixture
def make_yearly_cube(make_cube):
    """Build a 1D cube with one value and a ``year`` coordinate per point."""

    def _make_yearly_cube(values, years=None, start_year=1850, **metadata):
        if years is None:
            years = range(start_year, start_year + len(values))
        year_coord = AuxCoord(np.asarray(years), var_name="year")
        return make_cube(values, aux_coords_and_dims=[(year_coord, 0)], **metadata)

    return _make_yearly_cube


@pytest.fixture
def make_monthly_time_cube(make_cube):
    """Build a monthly time series with prescribed annual means."""

    def _make_monthly_time_cube(yearly_means, start_year=1850, **metadata):
        years = range(start_year, start_year + len(yearly_means))
        time_unit = Unit("days since 1850-01-01", calendar="gregorian")
        time_points = time_unit.date2num(
            [datetime.datetime(year, month, 15) for year in years for month in range(1, 13)]
        )
        time_coord = DimCoord(time_points, standard_name="time", units=time_unit)
        # Symmetric monthly samples preserve the requested mean while varying each month.
        data = np.concatenate([np.linspace(mean - 1.0, mean + 1.0, 12) for mean in yearly_means])
        return make_cube(data, dim_coords_and_dims=[(time_coord, 0)], **metadata)

    return _make_monthly_time_cube
