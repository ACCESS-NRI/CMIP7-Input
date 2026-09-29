"""End-to-end test of the real ACCESS-ESM1.6 solar generators."""

from pathlib import Path

import pytest

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.dispatch import generate_inputs
from cmip7_inputs.models.access_esm1p6 import MODEL_ID
from cmip7_inputs.core.context import GenerationRequest

from cmip7_inputs.models.access_esm1p6.generators.solar import generate_solar_historical
from cmip7_inputs.models.access_esm1p6.generators._constants import TODAY

def test_generate_solar_historical(tmp_path, create_solar_cube_mock):

    test_input_filepath = tmp_path / "test_input_solar_historical.nc"
    create_solar_cube_mock(yearly_means=[2.0, 6.0, 10.0], output_filepath=test_input_filepath)

    test_output_filename = "test_output_solar_historical.txt"
    test_request = GenerationRequest(
        model=MODEL_ID,
        experiment=experiments.HISTORICAL,
        input_name=input_names.SOLAR,
        output_dir=str(tmp_path),
        options={
            "input_filepath": test_input_filepath,
            "output_filename": test_output_filename,
        }
    )

    test_output_filepath = tmp_path / TODAY / test_output_filename
    generate_solar_historical(test_request)

    assert test_output_filepath.exists()
    # The output file is not a cube, but a text file
    with open(test_output_filepath, "r") as f:
            lines = f.readlines()
        
            expected_lines = [
                "1850 2.000\n",
                "1851 6.000\n",
                "1852 10.000\n",
            ]
            assert lines == expected_lines

def test_generate_inputs_unknown_combination_raises(
    tmp_path: Path,
) -> None:
    with pytest.raises(KeyError):
        generate_inputs(
            model=MODEL_ID,
            experiment="not-a-real-experiment",
            input_name="not-a-real-input",
            output_dir=tmp_path,
        )