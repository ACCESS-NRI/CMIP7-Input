from argparse import ArgumentParser

'''
This module provides functions to parse command line arguments for the CMIP7 ancil file processing scripts.
The entry points are defined in the flow.cylc workflow, and the arguments are passed to the scripts via the command line.
The values passed as arguments are defined either in the flow.cylc workflow or in the rose-suite.conf file. Or in the nci-gadi/variables.cylc.
'''

def dataset_parser():
    '''
    Return an ArgumentParser for CMIP7 dataset information.
    '''
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--dataset-version")
    parser.add_argument("--dataset-vdate")
    return parser


def dms_filename_parser(dms_ancil_filename=None):
    '''
    Return an ArgumentParser for DMS ancil filename information.
    '''
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--esm15-aerosol-version")
    # TODO: Remove the following argument. It is not used in the code.
    parser.add_argument("--dms-ancil-filename", default=dms_ancil_filename)
    return parser


def grid_parser():
    """
    Return an ArgumentParser for ESM1.5 grid ancil file processing.
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--esm-grid-rel-dirname")
    parser.add_argument("--esm15-grid-version")
    return parser


def path_parser():
    """
    Return an ArgumentParser for common directory path arguments.

    This parser is generic and can be reused by multiple
    CMIP7 ancillary-processing scripts that need to receive input or
    output directory locations from the command line.
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--ancil-target-dirname")
    parser.add_argument("--cmip7-source-data-dirname")
    parser.add_argument("--esm15-inputs-dirname")
    return parser


def percent_parser():
    '''
    Return an ArgumentParser for CMIP7 percentage ancil file processing.
    '''
    parser = ArgumentParser(add_help=False)
    # TODO: Remove the following two arguments.
    parser.add_argument("--percent-version") 
    parser.add_argument("--percent-vdate")
    # Corresponds to the date range of the aerosol biomass percentage e.g. '175001-202312'. This date range format means that the data is from January 1750 to December 2023.
    parser.add_argument("--percent-date-range")
    return parser


def common_parser():
    '''
    Return an ArgumentParser for common CMIP7 ancil file processing arguments.
    '''
    parser = ArgumentParser(
        parents=[path_parser(), grid_parser(), dataset_parser()], add_help=False
    )
    return parser
