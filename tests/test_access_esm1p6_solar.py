"""End-to-end test of the real ACCESS-ESM1.6 solar generators."""

import os
from pathlib import Path
from types import SimpleNamespace

import datetime
import numpy as np
import pytest
import iris

from CMIP7.esm1p6.ancil.lib.python.cmip7_inputs import experiments, input_names
from CMIP7.esm1p6.ancil.lib.python.cmip7_inputs.core.dispatch import generate_inputs
from CMIP7.esm1p6.ancil.lib.python.cmip7_inputs.models.access_esm1p6 import MODEL_ID

from CMIP7.esm1p6.ancil.lib.python.cmip7_inputs.models.access_esm1p6.generators.solar._common import (
    cmip7_solar_dirpath,
    SOLAR_ARRAY_BEG_YEAR,
    SOLAR_ARRAY_END_YEAR,
    cmip7_solar_year_mean,
    cmip7_solar_save,
)
from CMIP7.esm1p6.ancil.lib.python.cmip7_inputs.models.access_esm1p6.generators.solar import (
    cmip7_pi_solar_patch,
)
from CMIP7.esm1p6.ancil.lib.python.cmip7_inputs.models.access_esm1p6.generators._constants import REAL_MISSING_DATA_INDICATOR


def _make_iris_cube_from_yearly_values(yearly_values):
    """
    Build a real iris Cube containing monthly values from the yearly_values dict.

    Args:
        yearly_values: dict mapping year to list of values (one per timestep, e.g. per month)

    Returns:
        iris.cube.Cube with time coordinate using mid-month dates (day=15).
    """
    data = []
    times = []

    for year in sorted(yearly_values.keys()):
        for month, value in enumerate(yearly_values[year], start=1):
            times.append(datetime.date(year, month, 15))
            data.append(value)

    time_units = iris.unit.Unit("days since 1850-01-01", calendar="gregorian")
    time_coord = iris.coords.DimCoord(times, standard_name="time", units=time_units)

    return iris.cube.Cube(np.array(data), dim_coords_and_dims=[(time_coord, 0)])


@pytest.fixture
def solar_cube_fixture():
    """Fixture: reusable cube for solar year mean tests."""
    yearly_values = {
        1850: [1.0, 2.0, 3.0],
        1851: [5.0, 6.0, 7.0],
        1852: [10.0, 10.0, 10.0],
    }
    return _make_iris_cube_from_yearly_values(yearly_values)


@pytest.fixture
def tmp_atmosphere_dir(tmp_path):
    """Fixture: temporary directory with atmosphere subdirectory and input_atm.nml."""
    atm = tmp_path / "atmosphere"
    atm.mkdir()
    nml_file = atm / "input_atm.nml"
    nml_file.write_text("&coupling\n SC = 0.000\n/\n")
    return tmp_path


# ===================== cmip7_solar_dirpath tests =====================
def test_cmip7_solar_dirpath():
    """Test that cmip7_solar_dirpath constructs the correct path."""
    args = SimpleNamespace(
        cmip7_source_data_dirname="/data/input4MIPs",
        dataset_version="SOLARIS-HEPPA-CMIP-4-6",
        dataset_vdate="v20250219",
    )

    path = cmip7_solar_dirpath(args, "CMIP", "mon")

    assert path == Path(
        "/data/input4MIPs/CMIP/SOLARIS-HEPPA/"
        "SOLARIS-HEPPA-CMIP-4-6/atmos/mon/multiple/gn/v20250219"
    )


# ===================== cmip7_solar_year_mean tests =====================
def test_cmip7_solar_year_mean_full_range(solar_cube_fixture):
    """Test cmip7_solar_year_mean for full year range (1850-1852)."""
    result = cmip7_solar_year_mean(solar_cube_fixture, 1850, 1852)
    
    assert result[0] == 2.0
    assert result[1850 - SOLAR_ARRAY_BEG_YEAR] == 2.0
    assert result[1851 - SOLAR_ARRAY_BEG_YEAR] == 6.0
    assert result[1852 - SOLAR_ARRAY_BEG_YEAR] == 10.0
    assert result[-1] == REAL_MISSING_DATA_INDICATOR


def test_cmip7_solar_year_mean_uses_pi_value(solar_cube_fixture):
    """Test cmip7_solar_year_mean uses PI value for earlier years."""
    result = cmip7_solar_year_mean(solar_cube_fixture, 1851, 1851)
    
    assert result[1849 - SOLAR_ARRAY_BEG_YEAR] == 2.0
    assert result[1850 - SOLAR_ARRAY_BEG_YEAR] == 2.0
    assert result[1851 - SOLAR_ARRAY_BEG_YEAR] == 6.0


def test_cmip7_solar_year_mean_missing_after_end_year(solar_cube_fixture):
    """Test cmip7_solar_year_mean sets missing values after end year."""
    result = cmip7_solar_year_mean(solar_cube_fixture, 1850, 1851)
    
    assert result[1852 - SOLAR_ARRAY_BEG_YEAR] == REAL_MISSING_DATA_INDICATOR
    assert result[1853 - SOLAR_ARRAY_BEG_YEAR] == REAL_MISSING_DATA_INDICATOR


# ===================== cmip7_solar_save tests =====================
@pytest.mark.parametrize(
    "yearly_values,beg_year,end_year,filename",
    [
        ({1850: [1234.567], 1851: [0.0], 1852: [0.0]},1850,1850,"solar.txt"),
    ],
)
def test_cmip7_solar_save_writes_file(tmp_path, yearly_values, beg_year, end_year, filename):
    """Test that cmip7_solar_save creates file with expected content."""
    cube = _make_iris_cube_from_yearly_values(yearly_values)
    args = SimpleNamespace(save_filename=filename)
    cmip7_solar_save(args, cube=cube, beg_year=beg_year, end_year=end_year, save_dirpath=tmp_path)

    out = tmp_path / filename
    assert out.exists()
    assert out.parent == tmp_path
    content = out.read_text()
    assert "1850 1234.567" in content
    assert f"{SOLAR_ARRAY_END_YEAR} {REAL_MISSING_DATA_INDICATOR:.1f}" in content


# ===================== cmip7_pi_solar_patch tests =====================
@pytest.mark.parametrize(
    "solar_irradiance,expected_value",
    [
        (12.345678, "12.346"),
        (1361.603, "1361.603"),
    ],
)
def test_cmip7_pi_solar_patch_replaces_input_nml(
    tmp_atmosphere_dir, solar_irradiance, expected_value
):
    """Test that cmip7_pi_solar_patch updates SC value in input_atm.nml."""
    old_cwd = Path.cwd()
    try:
        os.chdir(tmp_atmosphere_dir)
        cmip7_pi_solar_patch(solar_irradiance)
    finally:
        os.chdir(old_cwd)

    nml_file = tmp_atmosphere_dir / "atmosphere" / "input_atm.nml"
    content = nml_file.read_text()
    assert "SC" in content
    assert expected_value in content


# ===================== generate_inputs tests =====================
@pytest.mark.parametrize(
    "experiment",
    [experiments.PI_CONTROL, experiments.HISTORICAL],
)
def test_generate_inputs_unknown_combination_raises(
    tmp_path: Path,
    experiment: str,
) -> None:
    """Test that generate_inputs raises KeyError for unknown combinations."""
    with pytest.raises(KeyError):
        generate_inputs(
            model=MODEL_ID,
            experiment="not-a-real-experiment",
            input_name="not-a-real-input",
            output_dir=tmp_path,
        )

