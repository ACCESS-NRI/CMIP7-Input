"""``cmip7-inputs`` command-line entry point."""

from __future__ import annotations

import argparse

from cmip7_inputs.core.dispatch import generate_inputs


def _parse_option(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError(
            f"invalid option {raw!r}, expected KEY=VALUE"
        )
    key, value = raw.split("=", 1)
    return key, value


def build_parser() -> argparse.ArgumentParser:
    """Build the ``cmip7-inputs`` argument parser."""
    parser = argparse.ArgumentParser(
        prog="cmip7-inputs",
        description=(
            "Generate a CMIP7 input file for a given model, "
            "experiment and input name."
        ),
    )
    parser.add_argument(
        "-m",
        "--model",
        required=True,
        help="Model id, e.g. access-esm1.6",
    )
    parser.add_argument(
        "-e",
        "--experiment",
        required=True,
        help="Experiment id, e.g. piControl",
    )
    parser.add_argument(
        "-n",
        "--input_name",
        dest="input_name",
        required=True,
        help="Input name, e.g. solar",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        dest="output_dir",
        default=".",
        help=(
            "Directory to write the generated input file to "
            "(default: %(default)s)"
        ),
    )
    parser.add_argument(
        "-O",
        "--option",
        dest="options",
        action="append",
        default=[],
        type=_parse_option,
        metavar="KEY=VALUE",
        help="Extra generator-specific option, may be repeated",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the ``cmip7-inputs`` CLI, returning the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    options = dict(args.options)

    try:
        generate_inputs(
            model=args.model,
            experiment=args.experiment,
            input_name=args.input_name,
            output_dir=args.output_dir,
            **options,
        )
    except KeyError as exc:
        parser.error(str(exc))
