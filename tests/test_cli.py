"""Tests for the ``cmip7-inputs`` command-line interface."""

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from cmip7_inputs.cli import _parse_option, main
from cmip7_inputs.models.access_esm1p6 import MODEL_ID


def test_parse_option_splits_key_value() -> None:
    assert _parse_option("key=value") == ("key", "value")


def test_parse_option_splits_only_on_first_equals() -> None:
    assert _parse_option("key=value=with=equals") == (
        "key",
        "value=with=equals",
    )


def test_parse_option_without_equals_raises() -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_option("not-a-key-value-pair")


@patch("cmip7_inputs.cli.generate_inputs")
def test_cli_generates_solar_file(
    mock_generate_inputs,
) -> None:
    main(
        [
            "-m",
            MODEL_ID,
            "-e",
            "piControl",
            "-n",
            "solar",
            "-o",
            "/some/output/dir",
        ]
    )
    mock_generate_inputs.assert_called_once()


def test_cli_unknown_combination_errors(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(
            [
                "-m",
                MODEL_ID,
                "-e",
                "not-real",
                "-n",
                "not-real",
                "-o",
                str(tmp_path),
            ]
        )
