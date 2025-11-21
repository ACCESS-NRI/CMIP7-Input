from argparse import ArgumentParser

from cmip7_ancil_argparse import common_parser


def parse_args():
    parser = ArgumentParser(
        parents=[common_parser()],
        prog="cmip7_HI_nitrogen_generate",
        description=(
            "Generate input files from CMIP7 historical nitrogen forcings"
        ),
    )
    parser.add_argument("--dataset-date-range-list")
    parser.add_argument("--save-filename")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
