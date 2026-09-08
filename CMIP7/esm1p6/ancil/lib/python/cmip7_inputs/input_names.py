"""Canonical input name identifiers used across the package.

These are the values accepted by the ``--input_name``/``-n`` CLI
option and used as keys when registering generators.
"""

# List of all available input_names in the format:
# <INPUT_NAME_KEY> = "<input_name_value>"
# The <INPUT_NAME_KEY> is used when registering a generator function
# with that input_name.
# The <input_name_value> is the value accepted by the
# `--input_name`/`-n` CLI option.
SOLAR = "solar"
