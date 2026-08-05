"""The ACCESS-ESM1.6 model.

Importing this package registers all of its generators. Add a new
input name for this model by creating a module under ``generators/``
and importing it from ``generators/__init__.py``.
"""

MODEL_ID = "access-esm1.6"

from cmip7_inputs.models.access_esm1p6 import generators  # noqa: F401

