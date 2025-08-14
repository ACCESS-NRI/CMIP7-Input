from argparse import ArgumentParser


def constraint_year_parser(beg_year=None, end_year=None):
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
            '--constraint-beg-year',
            type=int,
            default=beg_year)
    parser.add_argument(
            '--constraint-end-year',
            type=int,
            default=end_year)
    return parser


def dataset_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--dataset-version')
    parser.add_argument('--dataset-vdate')
    return parser


def dms_filename_parser(dms_ancil_filename=None):
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--esm15-aerosol-version')
    parser.add_argument(
            '--dms-ancil-filename',
            default=dms_ancil_filename)
    return parser


def grid_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--esm-grid-rel-dirname')
    parser.add_argument('--esm15-grid-version')
    return parser


def path_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--ancil-target-dirname')
    parser.add_argument('--cmip7-source-data-dirname')
    parser.add_argument('--esm15-inputs-dirname')
    return parser


def percent_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--percent-version')
    parser.add_argument('--percent-vdate')
    parser.add_argument('--percent-date-range')
    return parser


def common_parser():
    parser = ArgumentParser(
            parents=[
                path_parser(),
                grid_parser(),
                dataset_parser()],
            add_help=False)
    return parser
