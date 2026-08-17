"""ACCESS-ESM1.6 solar forcing generators.

Importing this package registers all of ACCESS-ESM1.6's solar
generators.
"""

from __future__ import annotations

from pathlib import Path

from cmip7_inputs import experiments, input_names
from cmip7_inputs.core.context import GenerationRequest
from cmip7_inputs.core.registry import registry
from cmip7_inputs.models.access_esm1p6 import MODEL_ID
from cmip7_inputs.models.access_esm1p6.generators.solar._common import (
    write_mock_solar_file,
)
from argparse import Namespace

from solar.cmip7_solar import (
    cmip7_solar_dirpath,
    load_cmip7_solar_cube,
)
from solar.cmip7_HI_solar_generate import cmip7_hi_solar_save


@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[experiments.PI_CONTROL, experiments.TEST],
)
def generate_solar_picontrol(request: GenerationRequest) -> Path:
    """Generate solar forcing input file for:
    model: ACCESS-ESM1.6
    experiment: piControl

    Placeholder processing that writes a text file describing the
    request instead of real solar forcing data.
    """
    return write_mock_solar_file(request)


def cmip7_hi_parse_args(request: GenerationRequest) -> Namespace:
    '''
    Parse the command line arguments for CMIP7 historical
    solar ancil file generation.
    '''
    return Namespace(**request.options)


@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[experiments.HISTORICAL,],
)
def generate_solar_historical(request: GenerationRequest):
    """Generate solar forcing input file for:
    model: ACCESS-ESM1.6
    experiment: historical
    """
    args = cmip7_hi_parse_args()

    dirpath = cmip7_solar_dirpath(args, "CMIP", "mon")
    filename = (
        "multiple_input4MIPs_solar_CMIP_"
        f"{args.dataset_version}_gn_"
        f"{args.dataset_date_range}.nc"
    )
    dataset_path = dirpath / filename

    solar_irradiance_cube = load_cmip7_solar_cube(dataset_path)

    cmip7_hi_solar_save(args, solar_irradiance_cube)
