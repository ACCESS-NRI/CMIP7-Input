"""The data every generator needs to produce an input file."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GenerationRequest:
    """Everything a generator needs to produce one input file.

    Attributes:
        model: Model id, e.g. ``"access-esm1.6"``.
        experiment: Experiment id, e.g. ``"piControl"``.
        input_name: Input name, e.g. ``"solar"``.
        output_dir: Directory the generator should write its output
            to.
        options: Generator-specific options (source data paths, target
            grid, date ranges, ...). Deliberately untyped for now.
    """

    model: str
    experiment: str
    input_name: str
    output_dir: Path
    options: dict[str, Any] = field(default_factory=dict)
