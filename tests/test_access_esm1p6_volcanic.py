"""End-to-end test of the real ACCESS-ESM1.6 volcanic generators."""

import os
from pathlib import Path
from types import SimpleNamespace

import cftime
import io
import numpy as np
import pytest

import iris
from CMIP7.esm1p6.ancil.lib.python.cmip7_inputs import experiments, input_names
from CMIP7.esm1p6.ancil.lib.python.cmip7_inputs.core.dispatch import generate_inputs
from CMIP7.esm1p6.ancil.lib.python.cmip7_inputs.models.access_esm1p6 import MODEL_ID

from CMIP7.esm1p6.ancil.lib.python.cmip7_inputs.models.access_esm1p6.generators.volcanic._common import (
    cmip7_volcanic_dirpath,
    constrain_to_wavelength,
    constrain_to_year_month,
    constrain_to_latitude_band,
    mean_over_latitudes,
    sum_over_height_layers,
    taper_saod,
    save_year_tapered_saod,
    SAOD_END_YEAR,
    MONTHS_IN_A_YEAR,
    NBR_OF_BANDS,
    NBR_TAPER_YEARS,
)


@pytest.fixture
def multi_month_cube():
    """Fixture: cube with multiple months of data."""
    dates = [
        cftime.datetime(2000, 1, 15, calendar="proleptic_gregorian"),
        cftime.datetime(2000, 2, 15, calendar="proleptic_gregorian"),
        cftime.datetime(2000, 3, 15, calendar="proleptic_gregorian"),
    ]
    data = np.array([1.0, 2.0, 3.0])
    time_coord = iris.coords.DimCoord(
        dates, standard_name="time", units=iris.unit.Unit("days since 2000-01-01")
    )
    return iris.cube.Cube(data, dim_coords_and_dims=[(time_coord, 0)])


@pytest.fixture
def multi_year_cube():
    """Fixture: cube spanning two years."""
    dates = [
        cftime.datetime(2000, 12, 15, calendar="proleptic_gregorian"),
        cftime.datetime(2001, 1, 15, calendar="proleptic_gregorian"),
        cftime.datetime(2001, 2, 15, calendar="proleptic_gregorian"),
    ]
    data = np.array([1.0, 2.0, 3.0])
    time_coord = iris.coords.DimCoord(
        dates, standard_name="time", units=iris.unit.Unit("days since 2000-01-01")
    )
    return iris.cube.Cube(data, dim_coords_and_dims=[(time_coord, 0)])


@pytest.fixture
def latitude_cube():
    """Fixture: cube with multiple latitude values."""
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    lats = np.array([60.0, 45.0, 15.0, -15.0, -60.0])
    lat_coord = iris.coords.DimCoord(lats, standard_name="latitude", units="degrees")
    return iris.cube.Cube(data, dim_coords_and_dims=[(lat_coord, 0)])


@pytest.fixture
def height_cube():
    """Fixture: cube with height coordinate and bounds."""
    data = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    heights = np.array([100.0, 500.0, 1000.0])
    height_bounds = np.array([
        [0.0, 300.0],
        [300.0, 750.0],
        [750.0, 1250.0],
    ])
    
    height_coord = iris.coords.DimCoord(
        heights,
        standard_name="height_above_mean_sea_level",
        units="m",
        bounds=height_bounds,
    )
    x_coord = iris.coords.DimCoord(np.array([0, 1]), long_name="x")
    
    return iris.cube.Cube(
        data,
        dim_coords_and_dims=[
            (height_coord, 0),
            (x_coord, 1),
        ],
    )


@pytest.fixture
def wavelength_cube():
    """Fixture: cube with radiation_wavelength coordinate."""
    data = np.array([1.0, 2.0, 3.0])
    wavelengths = np.array([400.0e-9, 550.0e-9, 700.0e-9])
    wl_coord = iris.coords.AuxCoord(
        wavelengths, standard_name="radiation_wavelength"
    )
    return iris.cube.Cube(data, aux_coords_and_dims=[(wl_coord, 0)])


def test_cmip7_volcanic_dirpath():
    """Test that cmip7_volcanic_dirpath constructs the correct path."""
    args = SimpleNamespace(cmip7_source_data_dirname="/data/input4MIPs")
    
    path = cmip7_volcanic_dirpath(
        args,
        activity="CMIP",
        period="mon",
        dataset_version="v20250219",
        dataset_vdate="v1",
    )
    
    expected = Path(
        "/data/input4MIPs/CMIP/uoexeter/v20250219/atmos/mon/ext/gnz/v1"
    )
    assert path == expected


def test_constrain_to_wavelength(wavelength_cube):
    """Test that constrain_to_wavelength filters by radiation_wavelength."""
    result = constrain_to_wavelength(wavelength_cube, 550.0e-9)
    
    assert result.data.size == 1
    assert result.data[0] == 2.0


def test_mean_over_latitudes():
    """Test that mean_over_latitudes computes weighted mean over latitude."""
    data = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    lats = np.array([-30.0, 0.0, 30.0])
    lons = np.array([0.0, 90.0])
    
    lat_coord = iris.coords.DimCoord(lats, standard_name="latitude", units="degrees")
    lon_coord = iris.coords.DimCoord(lons, standard_name="longitude", units="degrees")
    cube = iris.cube.Cube(
        data,
        dim_coords_and_dims=[
            (lat_coord, 0),
            (lon_coord, 1),
        ],
    )
    
    result = mean_over_latitudes(cube)
    
    assert result.ndim == 1
    assert result.shape == (2,)
    
    # Compute expected weighted mean
    cos_lats = np.cos(np.radians(lats))
    weights_norm = cos_lats / cos_lats.sum()
    
    expected_col0 = np.sum(data[:, 0] * weights_norm)
    expected_col1 = np.sum(data[:, 1] * weights_norm)
    
    assert np.isclose(result.data[0], expected_col0)
    assert np.isclose(result.data[1], expected_col1)


def test_sum_over_height_layers(height_cube):
    """Test that sum_over_height_layers sums weighted by layer height."""
    result = sum_over_height_layers(height_cube)
    
    assert result.ndim == 1
    assert result.shape == (2,)
    
    # Layer heights: 300, 450, 500
    expected_col0 = 1.0 * 300 + 3.0 * 450 + 5.0 * 500
    expected_col1 = 2.0 * 300 + 4.0 * 450 + 6.0 * 500
    assert np.isclose(result.data[0], expected_col0)
    assert np.isclose(result.data[1], expected_col1)


@pytest.mark.parametrize(
    "experiment",
    [experiments.PI_CONTROL, experiments.HISTORICAL],
)
def test_generate_inputs_unknown_combination_raises(
    tmp_path: Path,
    experiment: str,
) -> None:
    with pytest.raises(KeyError):
        generate_inputs(
            model=MODEL_ID,
            experiment="not-a-real-experiment",
            input_name="not-a-real-input",
            output_dir=tmp_path,
        )


def test_constrain_to_year_month_single_month(multi_month_cube):
    """Test that constrain_to_year_month extracts data for a single month."""
    result = constrain_to_year_month(multi_month_cube, 2000, 2)
    
    assert result.data.size == 1
    assert result.data[0] == 2.0


def test_constrain_to_year_month_december_wraps_year(multi_year_cube):
    """Test that December constraint wraps to January of next year."""
    result = constrain_to_year_month(multi_year_cube, 2000, 12)
    
    assert result.data.size == 1
    assert result.data[0] == 1.0


@pytest.mark.parametrize("band,expected_values", [
    (0, [1.0, 2.0]),  # 90 > lat >= 30
    (1, [2.0, 3.0]),  # 30 > lat >= 0
    (2, [3.0, 4.0]),  # 0 > lat >= -30
    (3, [4.0, 5.0]),  # -30 > lat >= -90
])
def test_constrain_to_latitude_band(latitude_cube, band, expected_values):
    """Test constrain_to_latitude_band for all four latitude bands."""
    result = constrain_to_latitude_band(latitude_cube, band=band)
    
    assert result.data.size == 2
    for val in expected_values:
        assert val in result.data


@pytest.fixture
def saod_beg_year_array():
    """Fixture: SAOD values at beginning of taper period."""
    return np.full((MONTHS_IN_A_YEAR, NBR_OF_BANDS), 1.0)


@pytest.fixture
def saod_end_year_array():
    """Fixture: SAOD values at end of taper period."""
    return np.full((MONTHS_IN_A_YEAR, NBR_OF_BANDS), 5.0)


def test_taper_saod_shape(saod_beg_year_array, saod_end_year_array):
    """Test that taper_saod returns array with correct shape."""
    volcanic_end_year = 2000
    result = taper_saod(volcanic_end_year, saod_beg_year_array, saod_end_year_array)
    
    expected_len = SAOD_END_YEAR - volcanic_end_year
    assert result.shape == (expected_len, MONTHS_IN_A_YEAR, NBR_OF_BANDS)


def test_taper_saod_interpolates_linearly(saod_beg_year_array, saod_end_year_array):
    """Test that taper_saod performs linear interpolation between endpoints."""
    volcanic_end_year = 2000
    result = taper_saod(volcanic_end_year, saod_beg_year_array, saod_end_year_array)
    
    # First year should be closer to end_year (5.0)
    # Ratio for first year (index 0): 1 / 10 = 0.1
    # Interpolated value: 5.0 + 0.1 * (1.0 - 5.0) = 5.0 - 0.4 = 4.6
    first_year_value = result[0, 0, 0]
    assert np.isclose(first_year_value, 4.6)
    
    # Last year of taper (index 9): ratio = 10 / 10 = 1.0
    # Interpolated value: 5.0 + 1.0 * (1.0 - 5.0) = 1.0
    last_taper_year_value = result[NBR_TAPER_YEARS - 1, 0, 0]
    assert np.isclose(last_taper_year_value, 1.0)


def test_taper_saod_constant_after_taper(saod_beg_year_array, saod_end_year_array):
    """Test that SAOD remains constant at beg_year value after taper period."""
    volcanic_end_year = 2000
    result = taper_saod(volcanic_end_year, saod_beg_year_array, saod_end_year_array)
    
    # After NBR_TAPER_YEARS (10 years), values should remain at beg_year (1.0)
    for index in range(NBR_TAPER_YEARS, result.shape[0]):
        assert np.isclose(result[index, 0, 0], 1.0)


def test_taper_saod_different_bands(saod_beg_year_array, saod_end_year_array):
    """Test that taper_saod handles different values for each latitude band."""
    volcanic_end_year = 2000
    
    # Create arrays with different values per band
    saod_beg = np.array([
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
    ])  # 2 months, 4 bands
    saod_end = np.array([
        [5.0, 6.0, 7.0, 8.0],
        [5.0, 6.0, 7.0, 8.0],
    ])
    
    result = taper_saod(volcanic_end_year, saod_beg, saod_end)
    
    # First year, first month, different bands
    first_year_month = result[0, 0, :]
    # Ratio = 0.1, so interpolation gives:
    # Band 0: 5.0 + 0.1 * (1.0 - 5.0) = 4.6
    # Band 1: 6.0 + 0.1 * (1.0 - 6.0) = 5.5
    # Band 2: 7.0 + 0.1 * (1.0 - 7.0) = 6.4
    # Band 3: 8.0 + 0.1 * (1.0 - 8.0) = 7.3
    expected = np.array([4.6, 5.5, 6.4, 7.3])
    assert np.allclose(first_year_month, expected)


def test_save_year_tapered_saod_format(saod_beg_year_array, saod_end_year_array):
    """Test that save_year_tapered_saod writes correctly formatted output."""
    volcanic_end_year = 2000
    tapered_array = taper_saod(volcanic_end_year, saod_beg_year_array, saod_end_year_array)
    
    output = io.StringIO()
    year = 2001  # First year after volcanic event
    save_year_tapered_saod(year, tapered_array, volcanic_end_year, output)
    
    content = output.getvalue()
    lines = content.strip().split('\n')
    
    # Should have MONTHS_IN_A_YEAR lines (12 for monthly data)
    assert len(lines) == MONTHS_IN_A_YEAR
    
    # Each line should start with year and month
    for month, line in enumerate(lines, start=1):
        assert line.startswith(f"{year:4d} {month:4d}")


def test_save_year_tapered_saod_values(saod_beg_year_array, saod_end_year_array):
    """Test that save_year_tapered_saod writes correct SAOD values."""
    volcanic_end_year = 2000
    tapered_array = taper_saod(volcanic_end_year, saod_beg_year_array, saod_end_year_array)
    
    output = io.StringIO()
    year = 2001
    save_year_tapered_saod(year, tapered_array, volcanic_end_year, output)
    
    content = output.getvalue()
    lines = content.strip().split('\n')
    first_line = lines[0]
    
    # Parse the first line to extract SAOD values
    parts = first_line.split()
    year_val = int(parts[0])
    month_val = int(parts[1])
    saod_values = [float(p) for p in parts[2:]]
    
    assert year_val == 2001
    assert month_val == 1
    assert len(saod_values) == NBR_OF_BANDS
    # All values should be close to 4.6 (interpolated value at first year)
    for saod_val in saod_values:
        assert np.isclose(saod_val, 4.6, atol=0.1)


@pytest.mark.parametrize("year_offset,expected_ratio", [
    (0, 0.1),   # First year: ratio = 1/10
    (4, 0.5),   # Fifth year: ratio = 5/10
    (9, 1.0),   # Last taper year: ratio = 10/10
])
def test_taper_saod_ratio_progression(
    saod_beg_year_array, saod_end_year_array, year_offset, expected_ratio
):
    """Test the ratio progression in taper_saod interpolation."""
    volcanic_end_year = 2000
    result = taper_saod(volcanic_end_year, saod_beg_year_array, saod_end_year_array)
    
    # Expected value: 5.0 + ratio * (1.0 - 5.0) = 5.0 - 4.0 * ratio
    expected_value = 5.0 - 4.0 * expected_ratio
    actual_value = result[year_offset, 0, 0]
    
    assert np.isclose(actual_value, expected_value)

@pytest.fixture
def sample_saod_cube():
    """Fixture: cube with SAOD data spanning multiple years and months."""
    data = np.random.rand(24, 4, 3)  # time, lat_bands, height_layers

    dates = []
    for year in [2000, 2001]:
        for month in range(1, 13):
            dates.append(cftime.datetime(year, month, 15, calendar="proleptic_gregorian"))

    time_coord = iris.coords.DimCoord(
        dates, standard_name="time", units=iris.unit.Unit("days since 2000-01-01")
    )
    lat_coord = iris.coords.DimCoord(
        np.array([0, 1, 2, 3]), long_name="latitude_band"
    )
    height_coord = iris.coords.DimCoord(
        np.array([15000, 18000, 21000]),
        standard_name="height_above_mean_sea_level",
        units="m",
        bounds=np.array([
            [12000, 16500],
            [16500, 19500],
            [19500, 22000],
        ]),
    )

    return iris.cube.Cube(
        data,
        dim_coords_and_dims=[
            (time_coord, 0),
            (lat_coord, 1),
            (height_coord, 2),
        ],
    )

