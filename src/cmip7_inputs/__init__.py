"""cmip7_inputs: generate CMIP7 input files for climate models."""

from cmip7_inputs.core.dispatch import generate_inputs
from cmip7_inputs.core.registry import registry

# Importing cmip7_inputs.models registers every model's generators as
# an import side effect (see cmip7_inputs/models/__init__.py).
from cmip7_inputs import models  # noqa: F401

__all__ = ["generate_inputs", "registry"]
