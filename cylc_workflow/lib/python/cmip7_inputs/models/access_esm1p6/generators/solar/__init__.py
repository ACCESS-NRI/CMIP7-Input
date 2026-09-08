"""ACCESS-ESM1.6 solar forcing generators.

Importing this package registers all of ACCESS-ESM1.6's solar
generators.
"""

from __future__ import annotations

from pathlib import Path

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.core.registry import registry
from cmip7_inputs.models.access_esm1p6 import MODEL_ID
from cmip7_inputs.models.access_esm1p6.generators.solar._common import (
    write_mock_solar_file,
)


@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[experiments.PI_CONTROL],
)
def generate_solar_picontrol(request: GenerationRequest) -> Path:
    """Generate solar forcing input file for:
    model: ACCESS-ESM1.6
    experiment: piControl

    Placeholder processing that writes a text file describing the
    request instead of real solar forcing data.
    """
    return write_mock_solar_file(request)


@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[experiments.HISTORICAL],
)
def generate_solar_historical(request: GenerationRequest) -> Path:
    """Generate solar forcing input file for:
    model: ACCESS-ESM1.6
    experiment: historical

    Placeholder processing that writes a text file describing the
    request instead of real solar forcing data.
    """
    return write_mock_solar_file(request)
