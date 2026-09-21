from argparse import ArgumentParser


def dataset_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--dataset-version")
    parser.add_argument("--dataset-vdate")
    return parser


def dms_filename_parser(dms_ancil_filename=None):
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--esm15-aerosol-version")
    parser.add_argument("--dms-ancil-filename", default=dms_ancil_filename)
    return parser


def pad_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--pad", action="store_true")
    return parser


def grid_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--esm-grid-rel-dirname")
    parser.add_argument("--esm15-grid-version")
    return parser


def path_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--ancil-target-dirname")
    parser.add_argument("--cmip7-source-data-dirname")
    parser.add_argument("--esm15-inputs-dirname")
    return parser


def percent_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--percent-version")
    parser.add_argument("--percent-vdate")
    parser.add_argument("--percent-date-range")
    return parser


def common_parser():
    parser = ArgumentParser(
        parents=[path_parser(), grid_parser(), dataset_parser()], add_help=False
    )
    return parser


def ext_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "--ext",
        action="store_true",
        default=False,
        help="Extend forcing from CMIP7_SM_END_YEAR (2100) to CMIP7_SM_EXT_END_YEAR (2150)",
    )
    parser.add_argument("--end-year", type=int, default=None, help="Override target end year")
    parser.add_argument("--dataset-ext-version", help="Version of extension dataset")
    parser.add_argument("--dataset-ext-vdate", help="Version date of extension dataset")
    parser.add_argument("--dataset-ext-date-range", help="Date range of extension dataset")
    parser.add_argument("--dataset-air-ext-version", help="Version of aircraft extension dataset")
    parser.add_argument("--dataset-air-ext-vdate", help="Version date of aircraft extension dataset")
    parser.add_argument("--dataset-air-ext-date-range", help="Date range of aircraft extension dataset")
    return parser
