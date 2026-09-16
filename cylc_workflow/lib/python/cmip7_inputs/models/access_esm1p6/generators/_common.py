""" This contains all the common functions for generating the ESM1.6 ancil files. """

from __future__ import annotations
from argparse import Namespace

from cmip7_inputs.core.context import GenerationRequest


def parse_additional_args(request: GenerationRequest) -> Namespace:
    '''
    Parse the command line additional arguments passed as `-O key=value`.
    '''
    return Namespace(**request.options)