from __future__ import annotations
from pathlib import Path

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.core.registry import registry
from cmip7_inputs.models.access_esm1p6 import MODEL_ID

from cmip7_inputs.models.access_esm1p6.generators.volcanic._common import (
    write_mock_volcanic_file
)

@registry.register(
    model=MODEL_ID,
    input_name=input_names.VOLCANIC,
    experiments=[experiments.HISTORICAL],
)
def generate_volcanic_historical(request: GenerationRequest) -> Path:
    """Generate volcanic forcing input file for:
    model: ACCESS-ESM1.6
    experiment: historical

    Placeholder processing that writes a text file describing the
    request instead of real volcanic forcing data.
    """
    return write_mock_volcanic_file(request)