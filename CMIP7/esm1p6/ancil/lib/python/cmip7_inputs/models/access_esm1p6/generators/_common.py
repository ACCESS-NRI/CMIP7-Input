from __future__ import annotations
from argparse import Namespace

from cmip7_inputs.core.context import GenerationRequest

def cmip7_parse_args(request: GenerationRequest) -> Namespace:
    '''
    Parse the command line arguments for CMIP7 historical
    solar ancil file generation.
    '''
    return Namespace(**request.options)