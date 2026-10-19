"""Unit tests for input4MIPs DRS Dataset and DatasetConfig abstractions."""

import os
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

# Ensure esm1p6_ancil is in sys.path for test execution
_LIB_DIR = Path(__file__).resolve().parent.parent / "lib" / "python"
_ANCIL_DIR = _LIB_DIR / "esm1p6_ancil"
for _path_str in (str(_LIB_DIR), str(_ANCIL_DIR)):
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

from dataset import (  # noqa: E402
    Dataset,
    DatasetConfig,
    DatasetDirname,
    DatasetFilename,
)


@pytest.fixture
def nitrogen_pi_facets() -> dict:
    """Fixture providing facets for Pre-Industrial Nitrogen Deposition."""
    return {
        "root": "/g/data/qv56/replicas",
        "activity_id": "input4MIPs",
        "mip_era": "CMIP7",
        "target_mip": "CMIP",
        "institution_id": "FZJ",
        "source_id": "FZJ-CMIP-nitrogen-1-2",
        "realm": "atmos",
        "frequency": "monC",
        "variable_id": "drynhx",
        "grid_label": "gn",
        "version": "v20251025",
        "dataset_category": "surfaceFluxes",
        "time_range": "185001-185012-clim",
    }


def test_dataset_dirname_assembly():
    """Test relative directory assembly with and without activity_id."""
    dirname = DatasetDirname(
        mip_era="CMIP7",
        target_mip="CMIP",
        institution_id="FZJ",
        source_id="FZJ-CMIP-nitrogen-1-2",
        realm="atmos",
        frequency="monC",
        variable_id="drynhx",
        grid_label="gn",
        version="v20251025",
        activity_id="input4MIPs",
    )
    expected_full = Path(
        "input4MIPs/CMIP7/CMIP/FZJ/FZJ-CMIP-nitrogen-1-2/"
        "atmos/monC/drynhx/gn/v20251025"
    )
    assert dirname.to_path(include_activity=True) == expected_full

    expected_no_act = Path(
        "CMIP7/CMIP/FZJ/FZJ-CMIP-nitrogen-1-2/atmos/monC/drynhx/gn/v20251025"
    )
    assert dirname.to_path(include_activity=False) == expected_no_act


def test_dataset_filename_assembly():
    """Test filename assembly including invariant fields with no time range."""
    fn_time = DatasetFilename(
        variable_id="drynhx",
        dataset_category="surfaceFluxes",
        target_mip="CMIP",
        source_id="FZJ-CMIP-nitrogen-1-2",
        grid_label="gn",
        time_range="185001-185012-clim",
        activity_id="input4MIPs",
        extension="nc",
    )
    expected_fn = (
        "drynhx_input4MIPs_surfaceFluxes_CMIP_FZJ-CMIP-nitrogen-1-2_gn_"
        "185001-185012-clim.nc"
    )
    assert fn_time.to_path() == Path(expected_fn)

    fn_no_time = DatasetFilename(
        variable_id="multiple",
        dataset_category="solar",
        target_mip="CMIP",
        source_id="SOLARIS-HEPPA-CMIP-4-4",
        grid_label="gn",
        time_range=None,
        activity_id="input4MIPs",
        extension="nc",
    )
    expected_solar = (
        "multiple_input4MIPs_solar_CMIP_SOLARIS-HEPPA-CMIP-4-4_gn.nc"
    )
    assert fn_no_time.to_path() == Path(expected_solar)


def test_dataset_path_resolution(nitrogen_pi_facets):
    """Test complete dataset path resolution and duplicate root prevention."""
    ds1 = Dataset.from_dict(nitrogen_pi_facets)
    expected_path = Path(
        "/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/FZJ/FZJ-CMIP-nitrogen-1-2/"
        "atmos/monC/drynhx/gn/v20251025/"
        "drynhx_input4MIPs_surfaceFluxes_CMIP_FZJ-CMIP-nitrogen-1-2_gn_"
        "185001-185012-clim.nc"
    )
    assert ds1.to_path() == expected_path
    assert os.fspath(ds1) == str(expected_path)
    assert str(ds1) == str(expected_path)

    # Test root already ending in 'input4MIPs' does not duplicate the segment
    facets_with_act_root = dict(nitrogen_pi_facets)
    facets_with_act_root["root"] = "/g/data/qv56/replicas/input4MIPs"
    ds2 = Dataset.from_dict(facets_with_act_root)
    assert ds2.to_path() == expected_path


def test_dataset_immutability(nitrogen_pi_facets):
    """Verify Dataset is frozen and cannot be mutated in place."""
    ds = Dataset.from_dict(nitrogen_pi_facets)
    with pytest.raises(FrozenInstanceError):
        ds.root = Path("/other/root")  # type: ignore


def test_dataset_modifiers(nitrogen_pi_facets):
    """Test explicit facet modifiers for single attributes."""
    ds = Dataset.from_dict(nitrogen_pi_facets)

    # Variable modifier
    ds_noy = ds.for_variable("drynoy")
    assert ds_noy.dirname.variable_id == "drynoy"
    assert ds_noy.filename.variable_id == "drynoy"
    assert "drynoy" in str(ds_noy.to_path())

    # Time range modifier
    ds_hist = ds.for_time_range("185001-202312")
    assert ds_hist.filename.time_range == "185001-202312"
    assert "185001-202312" in str(ds_hist.to_path())

    # Version modifier
    ds_v2 = ds.for_version("FZJ-CMIP-nitrogen-1-3", "v20260101")
    assert ds_v2.dirname.source_id == "FZJ-CMIP-nitrogen-1-3"
    assert ds_v2.dirname.version == "v20260101"
    assert ds_v2.filename.source_id == "FZJ-CMIP-nitrogen-1-3"
    assert "v20260101" in str(ds_v2.to_path())

    # Target MIP modifier
    ds_sm = ds.for_target_mip("ScenarioMIP")
    assert ds_sm.dirname.target_mip == "ScenarioMIP"
    assert ds_sm.filename.target_mip == "ScenarioMIP"
    assert "ScenarioMIP" in str(ds_sm.to_path())


def test_dataset_collection_helpers(nitrogen_pi_facets):
    """Test multi-species dict expansion and multi-chunk list expansion."""
    ds = Dataset.from_dict(nitrogen_pi_facets)
    species = ("drynhx", "drynoy", "wetnhx", "wetnoy")
    species_dict = ds.for_variables(species)

    assert isinstance(species_dict, dict)
    assert set(species_dict.keys()) == set(species)
    for sp, sp_ds in species_dict.items():
        assert sp_ds.dirname.variable_id == sp
        assert sp_ds.filename.variable_id == sp

    chunks = ["180001-184912", "185001-189912", "190001-194912"]
    chunk_list = ds.for_time_ranges(chunks)
    assert isinstance(chunk_list, list)
    assert len(chunk_list) == 3
    for i, tr in enumerate(chunks):
        assert chunk_list[i].filename.time_range == tr


def test_dataset_config_yaml_loading(tmp_path):
    """Test loading a DatasetConfig from a datasetconfig.yaml file."""
    yaml_content = """
root: /g/data/qv56/replicas
activity_id: input4MIPs
mip_era: CMIP7
target_mip: CMIP
institution_id: FZJ
source_id: FZJ-CMIP-nitrogen-1-2
realm: atmos
frequency: mon
grid_label: gn
version: v20251025
dataset_category: surfaceFluxes
time_range: 185001-202312
variables:
  - drynhx
  - drynoy
  - wetnhx
  - wetnoy
"""
    yaml_file = tmp_path / "datasetconfig.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    config = DatasetConfig.from_yaml(yaml_file)
    assert config.root == Path("/g/data/qv56/replicas")
    assert config.variables == ["drynhx", "drynoy", "wetnhx", "wetnoy"]
    assert config.time_ranges == ["185001-202312"]

    datasets = config.to_datasets_by_variable()
    assert len(datasets) == 4
    assert set(datasets.keys()) == {"drynhx", "drynoy", "wetnhx", "wetnoy"}
    expected_path = Path(
        "/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/FZJ/FZJ-CMIP-nitrogen-1-2/"
        "atmos/mon/wetnoy/gn/v20251025/"
        "wetnoy_input4MIPs_surfaceFluxes_CMIP_FZJ-CMIP-nitrogen-1-2_gn_"
        "185001-202312.nc"
    )
    assert datasets["wetnoy"].to_path() == expected_path


def test_dataset_config_sequence_expansion(tmp_path):
    """Test multi-chunk sequence expansion for aerosol time series."""
    yaml_content = """
root: /g/data/qv56/replicas
activity_id: input4MIPs
mip_era: CMIP7
target_mip: CMIP
institution_id: CEDS
source_id: CEDS-CMIP-aerosol-1-0
realm: atmos
frequency: mon
variable_id: SO2
grid_label: gn
version: v20250228
dataset_category: emissions
time_ranges:
  - 180001-184912
  - 185001-189912
  - 190001-194912
  - 195001-199912
  - 200001-202312
"""
    yaml_file = tmp_path / "datasetconfig.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    config = DatasetConfig.from_yaml(yaml_file)
    chunk_list = config.to_dataset_sequence()
    assert len(chunk_list) == 5
    assert chunk_list[0].filename.time_range == "180001-184912"
    assert chunk_list[-1].filename.time_range == "200001-202312"
    expected_chunk1 = Path(
        "/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/CEDS/CEDS-CMIP-aerosol-1-0/"
        "atmos/mon/SO2/gn/v20250228/"
        "SO2_input4MIPs_emissions_CMIP_CEDS-CMIP-aerosol-1-0_gn_"
        "185001-189912.nc"
    )
    assert chunk_list[1].to_path() == expected_chunk1


def test_dataset_config_sections_loading(tmp_path):
    """Test loading multi-section YAML files (e.g. ScenarioMIP streams)."""
    yaml_content = """
surface:
  root: /g/data/qv56/replicas
  target_mip: ScenarioMIP
  institution_id: IIASA-IAMC
  source_id: IIASA-IAMC-h-1-1-1
  realm: atmos
  frequency: mon
  variable_id: SO2
  grid_label: gn
  version: v20260409
  dataset_category: emissions
  time_range: 202201-210012

aircraft:
  root: /g/data/qv56/replicas
  target_mip: ScenarioMIP
  institution_id: IIASA-IAMC
  source_id: IIASA-IAMC-h-1-1-2
  realm: atmos
  frequency: mon
  variable_id: SO2
  grid_label: gn
  version: v20260624
  dataset_category: emissions
  time_range: 202201-210012
"""
    yaml_file = tmp_path / "datasetconfig.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    configs = DatasetConfig.from_yaml_sections(yaml_file)
    assert set(configs.keys()) == {"surface", "aircraft"}

    ds_surf = configs["surface"].to_dataset()
    ds_air = configs["aircraft"].to_dataset()

    assert ds_surf.dirname.source_id == "IIASA-IAMC-h-1-1-1"
    assert ds_air.dirname.source_id == "IIASA-IAMC-h-1-1-2"
    assert "v20260409" in str(ds_surf.to_path())
    assert "v20260624" in str(ds_air.to_path())


def test_dataset_config_from_yaml_with_section(tmp_path):
    """Test loading specific section via from_yaml(..., section=...)."""
    yaml_content = """
surface:
  root: /g/data/qv56/replicas
  activity_id: input4MIPs
  mip_era: CMIP7
  target_mip: ScenarioMIP
  institution_id: IIASA-IAMC
  source_id: IIASA-IAMC-h-1-1-1
  realm: atmos
  frequency: mon
  variable_id: SO2
  grid_label: gn
  version: v20260409
  dataset_category: emissions
  time_range: 202201-210012
aircraft:
  root: /g/data/qv56/replicas
  activity_id: input4MIPs
  mip_era: CMIP7
  target_mip: ScenarioMIP
  institution_id: IIASA-IAMC
  source_id: IIASA-IAMC-h-1-1-2
  realm: atmos
  frequency: mon
  variable_id: SO2
  grid_label: gn
  version: v20260624
  dataset_category: emissions
  time_range: 202201-210012
"""
    yaml_file = tmp_path / "datasetconfig.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    surf_cfg = DatasetConfig.from_yaml(yaml_file, section="surface")
    assert surf_cfg.dirname_facets["source_id"] == "IIASA-IAMC-h-1-1-1"

    with pytest.raises(KeyError, match="Section 'unknown' not found"):
        DatasetConfig.from_yaml(yaml_file, section="unknown")


def test_dataset_config_errors(tmp_path):
    """Test error handling for missing files and invalid configurations."""
    with pytest.raises(FileNotFoundError):
        DatasetConfig.from_yaml(tmp_path / "nonexistent.yaml")

    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("- not\n- a\n- dict\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a dictionary"):
        DatasetConfig.from_yaml(bad_yaml)

    empty_config = DatasetConfig.from_dict({"root": "/tmp"})
    with pytest.raises(ValueError, match="variable_id must be specified"):
        empty_config.to_dataset()

    with pytest.raises(ValueError, match="No variables specified"):
        empty_config.to_datasets_by_variable()

    with pytest.raises(ValueError, match="No time ranges specified"):
        empty_config.to_dataset_sequence()


def test_ghg_dataset_config_pi_hi():
    """Verify PI and HI GHG dataset configs produce expected DRS paths."""
    app_dir = Path(__file__).resolve().parent.parent / "app"
    for app_name in ("pi_ancil_ghg", "hi_ancil_ghg"):
        yaml_path = app_dir / app_name / "file" / "datasetconfig.yaml"
        config = DatasetConfig.from_yaml(yaml_path)
        assert len(config.variables) == 9
        assert "co2" in config.variables
        assert "ch4" in config.variables
        assert "n2o" in config.variables

        datasets = config.to_datasets_by_variable()
        assert len(datasets) == 9

        co2_path = datasets["co2"].to_path()
        expected = Path(
            "/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/CR/CR-CMIP-1-0-0/"
            "atmos/yr/co2/gm/v20250228/"
            "co2_input4MIPs_GHGConcentrations_CMIP_CR-CMIP-1-0-0_gm_"
            "1750-2022.nc"
        )
        assert co2_path == expected


def test_ghg_dataset_config_scenariomip():
    """Verify ScenarioMIP GHG dataset config loads all 7 scenarios and
    extensions."""
    yaml_path = (
        Path(__file__).resolve().parent.parent
        / "app"
        / "sm_ancil_ghg"
        / "file"
        / "datasetconfig.yaml"
    )
    scenarios = ("h", "hl", "m", "vl", "l", "ln", "ml")
    for scen in scenarios:
        cfg = DatasetConfig.from_yaml(yaml_path, section=scen)
        datasets = cfg.to_datasets_by_variable()
        assert len(datasets) == 9
        assert datasets["co2"].filename.time_range == "2022-2100"
        assert datasets["co2"].dirname.source_id == f"CR-{scen}-1-1-0"

        ext_cfg = DatasetConfig.from_yaml(yaml_path, section=f"{scen}-ext")
        ext_datasets = ext_cfg.to_datasets_by_variable()
        assert len(ext_datasets) == 9
        assert ext_datasets["co2"].filename.time_range == "2101-2200"
        assert ext_datasets["co2"].dirname.source_id == f"CR-{scen}-ext-1-1-0"

    h_cfg = DatasetConfig.from_yaml(yaml_path, section="h")
    h_path = h_cfg.to_datasets_by_variable()["co2"].to_path()
    expected_h = Path(
        "/g/data/qv56/replicas/input4MIPs/CMIP7/ScenarioMIP/CR/CR-h-1-1-0/"
        "atmos/yr/co2/gm/v20260327/"
        "co2_input4MIPs_GHGConcentrations_ScenarioMIP_CR-h-1-1-0_gm_"
        "2022-2100.nc"
    )
    assert h_path == expected_h
