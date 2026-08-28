"""cmip7_inputs: generate CMIP7 input files for climate models."""

# Importing cmip7_inputs.models registers every model's generators as
# an import side effect (see cmip7_inputs/models/__init__.py).
from cmip7_inputs_old import models  # noqa: F401
from cmip7_inputs_old.core.dispatch import generate_inputs
from cmip7_inputs_old.core.registry import registry

__all__ = ["generate_inputs", "registry"]
