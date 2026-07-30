"""Tests for the ``cmip7-inputs`` command-line interface."""

from pathlib import Path

import pytest

from cmip7_inputs.cli import main
from cmip7_inputs.models.access_esm1p6 import MODEL_ID


def test_cli_generates_solar_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(
        [
            "-m",
            MODEL_ID,
            "-e",
            "piControl",
            "-n",
            "solar",
            "-o",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    output_path = Path(capsys.readouterr().out.strip())
    assert output_path.exists()


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
