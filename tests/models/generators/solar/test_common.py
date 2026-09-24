import pytest
import iris
from iris.coords import AuxCoord, DimCoord
from iris.cube import Cube
from cf_units import Unit
import datetime
import numpy as np

from unittest.mock import patch, MagicMock

from cmip7_inputs.models.access_esm1p6.generators.solar._common import (
    load_solar_cube,
    compute_solar_yearly_mean,
    save_solar,
)
from cmip7_inputs.models.access_esm1p6.generators._constants import (
    REAL_MISSING_DATA_INDICATOR,
    HI_START_YEAR,
)

@pytest.fixture
def create_solar_cube_mock():
    def _create_solar_cube_mock(data=None, dim_coords=None, aux_coords=None):
        time_unit = Unit("days since 1850-01-01", calendar="gregorian")
        if dim_coords is None and aux_coords is None:
            
            start_year = 1850
            end_year = 1852
            n_months = (end_year - start_year + 1) * 12
            points = time_unit.date2num(
                        [datetime.datetime(start_year+i//12, i%12+1, 15) for i in range(n_months)]
                    )

            time = DimCoord(
                points,
                standard_name="time",
                units=time_unit,
            )

            data = np.random.rand(n_months)  # Random data for testing

            dim_coords = [(time, 0)]

        cube = Cube(
            data,
            dim_coords_and_dims=dim_coords,
            aux_coords_and_dims=aux_coords,
        )

        return cube
    return _create_solar_cube_mock


# def test_load_solar_cube(tmp_path):
#     """Test that load_solar_cube correctly loads a cube from a file."""
#     # Create a temporary file with a simple iris cube

#     cube_mock = create_solar_cube_mock()
#     filepath = tmp_path / "test_solar.nc"
#     iris.save(cube_mock, str(filepath))

#     # Load the cube using the function under test
#     loaded_cube = load_solar_cube(str(filepath))

#     # Check that the loaded cube matches the original cube
#     assert loaded_cube.shape == cube_mock.shape
#     assert np.allclose(loaded_cube.data, cube_mock.data)

# # ===================== cmip7_solar_year_mean tests =====================
# def test_compute_solar_yearly_mean_full_range(create_solar_cube_mock):
#     """Test compute_solar_yearly_mean for full year range (1850-1852)."""
#     cube_mock = create_solar_cube_mock()
    
#     assert cube_mock[0] == 2.0
#     assert cube_mock[1850 - HI_START_YEAR] == 2.0
#     assert cube_mock[1851 - HI_START_YEAR] == 6.0
#     assert cube_mock[1852 - HI_START_YEAR] == 10.0
#     #assert cube_mock[-1] == REAL_MISSING_DATA_INDICATOR


# def test_compute_solar_yearly_mean_before_start_year(create_solar_cube_mock):
#     """Test compute_solar_yearly_mean sets missing values before start year."""
#     result = compute_solar_yearly_mean(create_solar_cube_mock, 1850, 1851)
    
#     assert result[1849 - HI_START_YEAR] == REAL_MISSING_DATA_INDICATOR
#     assert result[1848 - HI_START_YEAR] == REAL_MISSING_DATA_INDICATOR

# def test_compute_solar_yearly_mean_after_end_year(create_solar_cube_mock):
#     """Test compute_solar_yearly_mean sets missing values after end year."""
#     result = compute_solar_yearly_mean(create_solar_cube_mock, 1850, 1851)
    
#     assert result[1852 - HI_START_YEAR] == REAL_MISSING_DATA_INDICATOR
#     assert result[1853 - HI_START_YEAR] == REAL_MISSING_DATA_INDICATOR

# def test_compute_solar_yearly_mean_with_missing_data(create_solar_cube_mock):
#     """Test compute_solar_yearly_mean handles NaN values correctly."""
#     # Introduce NaN values for 1851
#     create_solar_cube_mock.data[3:6] = np.nan  # Assuming monthly data, indices 3-5 correspond to 1851

#     result = compute_solar_yearly_mean(create_solar_cube_mock, 1850, 1852)
    
#     assert result[1850 - HI_START_YEAR] == 2.0
#     assert result[1851 - HI_START_YEAR] == REAL_MISSING_DATA_INDICATOR
#     assert result[1852 - HI_START_YEAR] == 10.0

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
    
    