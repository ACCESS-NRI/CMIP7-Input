"""Tests for the reusable Iris cube factory fixtures."""

import numpy as np
from iris.coords import DimCoord


def test_make_cube_with_latitude_and_longitude_coordinates(make_cube):
    latitude = DimCoord([-45.0, 45.0], standard_name="latitude", units="degrees")
    longitude = DimCoord([0.0, 120.0, 240.0], standard_name="longitude", units="degrees")
    expected_data = np.arange(6).reshape(2, 3)

    cube = make_cube(
        expected_data,
        dim_coords_and_dims=[(latitude, 0), (longitude, 1)],
        long_name="sample field",
    )

    np.testing.assert_array_equal(cube.data, expected_data)
    np.testing.assert_array_equal(cube.coord("latitude").points, [-45.0, 45.0])
    np.testing.assert_array_equal(cube.coord("longitude").points, [0.0, 120.0, 240.0])
    assert cube.name() == "sample field"
