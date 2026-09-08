"""The single entry point used to generate a CMIP7 input file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.core.registry import registry


def generate_inputs(
    *,
    model: str,
    experiment: str,
    input_name: str,
    output_dir: str | Path,
    **options: Any,
) -> Path:
    """Generate one CMIP7 input file.

    Resolves the matching generator from the registry and calls it
    with a :class:`~cmip7_inputs.core.context.GenerationRequest` built
    from the given arguments.

    Importing ``cmip7_inputs`` registers every model's generators (via
    ``cmip7_inputs.models``), so the registry is fully populated by
    the time this runs.
    """
    generator = registry.resolve(
        model=model, input_name=input_name, experiment=experiment
    )
    request = GenerationRequest(
        model=model,
        experiment=experiment,
        input_name=input_name,
        output_dir=Path(output_dir),
        options=options,
    )
    return generator(request)
