"""ACCESS-ESM1.6 solar forcing input generators."""

from __future__ import annotations

from pathlib import Path

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.core.registry import registry

from .. import MODEL_ID


@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[experiments.PI_CONTROL],
)
def generate_solar_picontrol(request: GenerationRequest) -> Path:
    """Generate solar forcing input file for:
    model: ACCESS-ESM1.6
    experiment: piControl

    Placeholder processing that writes a text file describing the request
    instead of real solar forcing data.
    """
    request.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = request.output_dir / (
        f"{request.model}_{request.experiment}_{request.input_name}.txt"
    )
    output_path.write_text(
        "Mock CMIP7 input file\n"
        f"model: {request.model}\n"
        f"experiment: {request.experiment}\n"
        f"input_name: {request.input_name}\n"
        f"options: {request.options}\n"
    )
    return output_path

@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[experiments.HISTORICAL],
)
def generate_solar_historical(request: GenerationRequest) -> Path:
    """Generate solar forcing input file for:
    model: ACCESS-ESM1.6
    experiment: historical

    Placeholder processing that writes a text file describing the request
    instead of real solar forcing data.
    """
    request.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = request.output_dir / (
        f"{request.model}_{request.experiment}_{request.input_name}.txt"
    )
    output_path.write_text(
        "Mock CMIP7 input file\n"
        f"model: {request.model}\n"
        f"experiment: {request.experiment}\n"
        f"input_name: {request.input_name}\n"
        f"options: {request.options}\n"
    )
    return output_path
