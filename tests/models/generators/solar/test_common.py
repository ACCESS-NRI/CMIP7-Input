import pytest
import iris
from iris.coords import AuxCoord
import numpy as np

from unittest.mock import patch

from cmip7_inputs.models.access_esm1p6.generators.solar._common import (
    load_solar_cube,
    compute_solar_yearly_mean,
    save_solar,
)
from cmip7_inputs.models.access_esm1p6.generators._constants import REAL_MISSING_DATA_INDICATOR


# ===================== load_solar_cube tests =====================
def test_load_solar_cube(tmp_path, create_solar_cube_mock):
    """Test that load_solar_cube loads only the solar_irradiance cube from a file."""
    
    filepath = tmp_path / "test_solar.nc"
    # Inside the written file it contains a second cube that should be ignored
    solar_cube = create_solar_cube_mock(yearly_means=[2.0, 6.0, 10.0], output_filepath=filepath)

    loaded_cube = load_solar_cube(str(filepath))

    assert loaded_cube.name() == "solar_irradiance"
    np.testing.assert_allclose(loaded_cube.data, solar_cube.data)
    np.testing.assert_allclose(loaded_cube.coord("time").points, solar_cube.coord("time").points)

# ===================== solar_year_mean tests =====================
def test_compute_solar_yearly_mean_full_range(create_solar_cube_mock):
    """Test compute_solar_yearly_mean for full year range (1850-1852)."""
    input_cube = create_solar_cube_mock(yearly_means=[2.0, 6.0, 10.0])

    result = compute_solar_yearly_mean(input_cube, 1850, 1852)

    np.testing.assert_array_equal(result.coord("year").points, [1850, 1851, 1852])
    np.testing.assert_allclose(result.data, [2.0, 6.0, 10.0])

@pytest.mark.parametrize(
    "start_year, end_year, expected_years, expected_means",
    [
        (1850, 1852, [1850, 1851, 1852], [2.0, 6.0, 10.0]), #extra years before
        (1848, 1850, [1848, 1849, 1850], [-2.0, 1.0, 2.0]), #extra years after
        (1849, 1851, [1849, 1850, 1851], [1.0, 2.0, 6.0]), #extra years on both sides
        (1851, 1851, [1851], [6.0]), #single year
    ],
    ids=["before_start_year", "after_end_year", "both_sides", "single_year"],
)
def test_compute_solar_yearly_mean_excludes_years_outside_range(
    create_solar_cube_mock, start_year, end_year, expected_years, expected_means
):
    """Test compute_solar_yearly_mean excludes years outside [start_year, end_year]."""
    # cube covering 1848-1852
    input_cube = create_solar_cube_mock(yearly_means=[-2.0, 1.0, 2.0, 6.0, 10.0], start_year=1848)

    result = compute_solar_yearly_mean(input_cube, start_year, end_year)

    np.testing.assert_array_equal(result.coord("year").points, expected_years)
    np.testing.assert_allclose(result.data, expected_means)


def test_compute_solar_yearly_mean_with_missing_data(create_solar_cube_mock):
    """Test compute_solar_yearly_mean replaces NaN yearly means with the missing data indicator."""
    input_cube = create_solar_cube_mock(yearly_means=[2.0, 6.0, 10.0])
    # Introduce NaN values in April-June 1851 (monthly indices 15-17)
    input_cube.data[15:18] = np.nan

    result = compute_solar_yearly_mean(input_cube, 1850, 1852)

    np.testing.assert_array_equal(result.coord("year").points, [1850, 1851, 1852])
    # a single NaN month makes the yearly mean NaN, so 1851 is flagged as missing
    np.testing.assert_allclose(result.data, [2.0, REAL_MISSING_DATA_INDICATOR, 10.0])

# ===================== save_solar tests =====================
@patch("cmip7_inputs.models.access_esm1p6.generators.solar._common.compute_solar_yearly_mean")
def test_save_solar(mock_compute_solar_yearly_mean, tmp_path, create_solar_cube_mock):
    """Test that save_solar calls compute_solar_yearly_mean with correct arguments."""

    aux_coord = [(AuxCoord([1850,1851,1852],var_name='year'),0)]
    data = np.array([2.0, REAL_MISSING_DATA_INDICATOR, 10.0])

    # cube with one value per year
    cube_mock = create_solar_cube_mock(data, aux_coords=aux_coord)
    mock_compute_solar_yearly_mean.return_value = cube_mock

    # mock_directory is added to test the creation of the directory
    output_file = tmp_path / "mock_directory" / "solar_output.txt"

    input_cube = create_solar_cube_mock()
    save_solar(output_file, input_cube, 1850, 1852)

    mock_compute_solar_yearly_mean.assert_called_once_with(input_cube, 1850, 1852)

    with open(output_file, "r") as f:
        lines = f.readlines()
    
        expected_lines = [
            "1850 2.000\n",
            "1851 -1073741824.0\n",  # Missing data indicator for NaN
            "1852 10.000\n",
        ]
        assert lines == expected_lines
    
    