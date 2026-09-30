"""Tests for the registration/fallback mechanics of GeneratorRegistry.

These are independent of any real model, so it's easy to convince
yourself the mechanics are right without wading through real
processing code.
"""

import pytest

from cmip7_inputs.core.dispatch import generate_inputs


@pytest.mark.parametrize(
    "model, experiment, input_name",
    [
        ("unknown-model", "historical", "solar"),
        ("access-esm1.6", "unknown-experiment", "solar"),
        ("access-esm1.6", "historical", "unknown-input"),
    ],
    ids=[
        "unknown-model",
        "unknown-experiment",
        "unknown-input",
    ],
)
def test_generate_inputs_unknown_combination_raises(tmp_path, model, experiment, input_name):
    with pytest.raises(KeyError):
        generate_inputs(
            model=model,
            experiment=experiment,
            input_name=input_name,
            output_dir=tmp_path,
        )
