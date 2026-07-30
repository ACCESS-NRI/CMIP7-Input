"""End-to-end test of the real ACCESS-ESM1.6 solar/piControl path."""

from pathlib import Path

import pytest

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.dispatch import generate_inputs
from cmip7_inputs.models.access_esm1p6 import MODEL_ID


def test_generate_picontrol_solar_writes_file(tmp_path: Path) -> None:
    output_path = generate_inputs(
        model=MODEL_ID,
        experiment=experiments.PI_CONTROL,
        input_name=input_names.SOLAR,
        output_dir=tmp_path,
    )

    assert output_path.exists()
    assert output_path.parent == tmp_path

    content = output_path.read_text()
    assert MODEL_ID in content
    assert experiments.PI_CONTROL in content
    assert input_names.SOLAR in content


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
