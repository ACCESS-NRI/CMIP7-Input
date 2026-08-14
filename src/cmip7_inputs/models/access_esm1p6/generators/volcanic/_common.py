from __future__ import annotations

from cmip7_inputs.core.context import GenerationRequest

def write_mock_volcanic_file(request: GenerationRequest, dirpath: Path = None, dataset_path: Path = None) -> Path:
    """Write a placeholder file describing the request.

    Shared by every ACCESS-ESM1.6 volcanic generator until real volcanic
    forcing processing is implemented.
    """
    request.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = request.output_dir / (
        f"{request.model}_{request.experiment}_{request.input_name}.txt"
    )
    output_path.write_text(
        "Mock CMIP7 input file\n"
        f"model: {request.model}\n"
        f"experiment: {request.experiment}\n"
        f"input_name: {request.input_name}\n"
        f"options: {request.options}\n"

        # Historical volcanic forcing options
        f"dataset-version: {request.options['dataset-version']}\n"
        f"dataset-vdate: {request.options['dataset-vdate']}\n"
        f"dataset-date-range: {request.options['dataset-date-range']}\n"
        f"save-filename: {request.options['save-filename']}\n"
        

        f"cmip7-source-data-dirname: {request.options['cmip7-source-data-dirname']}\n"
        f"ancil_target_dirname: {request.options['ancil_target_dirname']}\n"

        "Dirpath function test:\n"
        f"dirpath: {dirpath}\n"
        f"dataset_path: {dataset_path}\n"
        # ScenarioMIP
        #f"scenario: {request.options['scenario']}\n"
        
    )
    return output_path
