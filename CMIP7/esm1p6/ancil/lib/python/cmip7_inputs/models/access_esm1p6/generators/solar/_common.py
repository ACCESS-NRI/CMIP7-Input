"""Shared helpers for ACCESS-ESM1.6 solar generators."""

from __future__ import annotations

from pathlib import Path

from cmip7_inputs.core.context import GenerationRequest


def write_mock_solar_file(request: GenerationRequest) -> Path:
    """Write a placeholder file describing the request.

    Shared by every ACCESS-ESM1.6 solar generator until real solar
    forcing processing is implemented.
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
