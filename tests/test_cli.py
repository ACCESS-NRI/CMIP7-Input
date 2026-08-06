"""Tests for the ``cmip7-inputs`` command-line interface."""

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cmip7_inputs.cli import _parse_option, main
from cmip7_inputs.core.registry import registry


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


@pytest.mark.parametrize(
    ("model", "experiment", "input_name"),
    [
        ("access-esm1.6", "picontrol", "solar"),
        ("access-esm1.6", "historical", "solar"),
    ],
)
def test_cli_valid_combination_dispatches(
    model: str,
    experiment: str,
    input_name: str,
    tmp_path: Path,
) -> None:
    """Check the CLI accepts a valid combination and dispatches it.

    Wraps ``registry.resolve`` so the real (model, input_name,
    experiment) lookup still runs -- confirming it's a genuinely
    registered combination, and raising otherwise -- but swaps in a
    mock generator so whichever registered function it resolves to
    never actually runs.
    """
    real_resolve = registry.resolve

    def resolve_with_mock_generator(**kwargs):
        real_resolve(**kwargs)  # raises if not a real combination
        return MagicMock()

    with patch.object(
        registry, "resolve", side_effect=resolve_with_mock_generator
    ) as mock_resolve:
        main(
            [
                "-m",
                model,
                "-e",
                experiment,
                "-n",
                input_name,
                "-o",
                str(tmp_path),
            ]
        )

    mock_resolve.assert_called_once_with(
        model=model, input_name=input_name, experiment=experiment
    )


@pytest.mark.parametrize(
    ("model", "experiment", "input_name"),
    [
        ("access-esm1.6", "picontrol", "not-real"),
        ("access-esm1.6", "not-real", "solar"),
        ("not-real", "picontrol", "solar"),
    ],
)
def test_cli_not_valid_combinations_error(
    model: str,
    experiment: str,
    input_name: str,
    tmp_path: Path,
) -> None:
    """Check the CLI errors out for a combination that isn't registered.

    Wraps ``registry.resolve`` so the real (model, input_name,
    experiment) lookup still runs -- confirming it's not a genuinely
    registered combination -- but swaps in a mock generator so
    whichever registered function it might otherwise resolve to never
    actually runs.
    """
    real_resolve = registry.resolve

    def resolve_with_mock_generator(**kwargs):
        real_resolve(**kwargs)  # raises if not a real combination
        return MagicMock()

    with (
        patch.object(
            registry, "resolve", side_effect=resolve_with_mock_generator
        ) as mock_resolve,
        pytest.raises(SystemExit),
    ):
        main(
            [
                "-m",
                model,
                "-e",
                experiment,
                "-n",
                input_name,
                "-o",
                str(tmp_path),
            ]
        )

    mock_resolve.assert_called_once_with(
        model=model, input_name=input_name, experiment=experiment
    )
