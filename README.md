> [!IMPORTANT] 
> This repository is temporary and is a private copy of the public [CMIP7-Input](https://github.com/ACCESS-NRI/CMIP7-Input) public repository. 
> It was created to allow porting on GitHub the CMIP7 workflow, which might have licensing issue being added directly to a public GitHub repository. 
> Once the potential licensing issues have been sorted out and the CMIP7 inputs workflow is added to the CMIP7-Input public repository, this repository can be deleted.
> For further information about this repo, please check the public [CMIP7-Input](https://github.com/ACCESS-NRI/CMIP7-Input) repo.


# cmip7_inputs
Generate a CMIP7 input file for a given model, experiment and input name.

## Development

### How to install
To install a development version of the package, we suggest using `micromamba`.

After [installing micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html), from this repo's root directory run the following command:

```
micromamba create -n cmip7_inputs python==3.11 -y
micromamba activate cmip7_inputs
python -m pip install .[dev]
```

### Run tests
Run tests with:
```
micromamba run -n cmip7_inputs pytest
```

### How it works
- `cmip7_inputs/core/context.py::GenerationRequest` carries model, experiment, input_name, output_dir, and an open options dict for generator-specific kwargs.
- `cmip7_inputs/core/registry.py::GenerationRegistry` maps `(model, input_name, experiment) -> generator`, populated via the `@registry.register(...)` decorator as an import side effect (nothing registered by hand centrally). Passing `experiments=[...]` registers for specific experiments (letting several experiments share one generator); `experiments=None` registers a default fallback for any experiment.
- `generate_inputs(model=..., experiment=..., input_name=..., output_dir=..., **options)` is the internal entry point function. It resolves the generator and calls it.
- The CLI (`cmip7-inputs -m ... -e ... -n ... -o ...  [-O KEY=VALUE [...]]`) wraps `generate_inputs`, plus a repeatable `-O KEY=VALUE` flag for generator-specific options.

### Adding a new model/experiment/input_name
**New model**
1. Add a new subpackage under `models/` (e.g., `models/my_new_model/__init__.py`);
2. In the new model subpackage `__init__.py` add the `MODEL_ID` and import its generators;
3. Import the model from the `models/__init__.py`.

**New input_name**
1. For a specific model, add a new module under its generators (e.g., `models/access_esm1p6/generators/my_new_input/__init__.py`) where you define all its generator functions;
2. Add a new `<INPUT_NAME_KEY> = "<input_name>"` line in `input_names.py`. The `<INPUT_NAME_KEY>` is used when registering a generator function with that input_name. The `<input_name>` is the value accepted by the `--input_name`/`-n` CLI option;
3. Import the input_name from the `models/<model>/generators/__init__.py`.

**New experiment**
1. Add a new `<EXPERIMENT_KEY> = "<experiment_name>"` line in `experiments.py`. The `<EXPERIMENT_KEY>` is used when registering a generator function with that experiment. The `<experiment_name>` is the value accepted by the `--experiment`/`-e` CLI option;
2. For a specific model and input_name, add the `<EXPERIMENT_KEY>` to any generator function who should be associated with that experiment (or create a new one) in `models/<model>/generators/<input_name>/__init__.py`.