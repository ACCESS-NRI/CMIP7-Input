"""End-to-end test of the real ACCESS-ESM1.6 solar generators."""

import iris

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.models.access_esm1p6 import MODEL_ID
from cmip7_inputs.models.access_esm1p6.generators._constants import TODAY
from cmip7_inputs.models.access_esm1p6.generators.solar import generate_solar_historical


def test_generate_solar_historical(tmp_path, make_monthly_time_cube):
    """
    Test the generate_solar_historical generator function
    """
    expected_lines = [
        "1850 2.000\n",
        "1851 6.000\n",
        "1852 10.000\n",
    ]

    test_input_filepath = tmp_path / "test_input_solar_historical.nc"
    # Create mock input netcdf
    iris.save(
        make_monthly_time_cube([2.0, 6.0, 10.0], var_name="solar_irradiance"),
        test_input_filepath,
    )

    test_output_filename = "test_output_solar_historical.txt"
    test_output_filepath = tmp_path / TODAY / test_output_filename
    test_request = GenerationRequest(
        model=MODEL_ID,
        experiment=experiments.HISTORICAL,
        input_name=input_names.SOLAR,
        output_dir=str(tmp_path),
        options={
            "input_filepath": test_input_filepath,
            "output_filename": test_output_filename,
        },
    )

    generate_solar_historical(test_request)

    assert test_output_filepath.exists()
    with open(test_output_filepath) as f:
        lines = f.readlines()
    assert lines == expected_lines
