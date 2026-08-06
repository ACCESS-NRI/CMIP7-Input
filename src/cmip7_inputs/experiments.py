"""Canonical experiment identifiers used across the package.

These are the values accepted by the ``--experiment``/``-e`` CLI
option and used as keys when registering generators.
"""

# List of all available experiments in the format:
# <EXPERIMENT_KEY> = "<experiment_value>"
# The <EXPERIMENT_KEY> is used when registering a generator function
# with that experiment.
# The <experiment_value> is the value accepted by the
# `--experiment`/`-e` CLI option.
PI_CONTROL = "picontrol"
HISTORICAL = "historical"
