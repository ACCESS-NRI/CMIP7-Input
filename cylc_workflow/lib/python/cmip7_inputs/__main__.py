"""Allow running the CLI via ``python -m cmip7_inputs``."""

from __future__ import annotations

import sys

from cmip7_inputs.cli import main

if __name__ == "__main__":
    sys.exit(main())
