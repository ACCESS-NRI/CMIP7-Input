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
from cmip7_inputs.models.access_esm1p6.generators._constants import HI_END_YEAR, HI_START_YEAR, TODAY
from cmip7_inputs.models.access_esm1p6.generators.solar._common import (
    load_solar_cube,
    save_solar,
)

# ------------------------------------------------------
# ------------------- HISTORICAL -----------------------
# ------------------------------------------------------
# cmip7-inputs -m access-esm1.6 -n solar -e historical -o output_test
# -O dataset-version=SOLARIS-HEPPA-CMIP-4-6 -O dataset-vdate=v20250219
# -O dataset-date-range=185001-202312 -O save-filename=TSI_CMIP7_ESM
# -O cmip7-source-data-dirname=/input_test -O ancil_target_dirname=/ancil_dirname


@registry.register(
    model=MODEL_ID,
    input_name=input_names.SOLAR,
    experiments=[
        experiments.HISTORICAL,
    ],
)
def generate_solar_historical(request: GenerationRequest):
    """Generate solar forcing input file for:
    model: ACCESS-ESM1.6
    experiment: historical
    """

    solar_irradiance_cube = load_solar_cube(request.options["input_filepath"])
    historical_save_filepath = Path(request.output_dir) / TODAY / request.options["output_filename"]

    # Save the Total Solar Irradiance values for each year into a text file.
    save_solar(historical_save_filepath, solar_irradiance_cube, HI_START_YEAR, HI_END_YEAR)


# ------------------- PI CONTROL -----------------------
# ------------------------------------------------------

# @registry.register(
#     model=MODEL_ID,
#     input_name=input_names.SOLAR,
#     experiments=[experiments.PI_CONTROL],
# )
# def generate_solar_picontrol(request: GenerationRequest) -> Path:
#     """Generate solar forcing input file for:
#     model: ACCESS-ESM1.6
#     experiment: piControl

#     Placeholder processing that writes a text file describing the
#     request instead of real solar forcing data.
#     """
#     return write_mock_solar_file(request)
