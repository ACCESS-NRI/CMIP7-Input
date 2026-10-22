"""Data Reference Syntax (DRS) dataset abstractions for input4MIPs forcings."""

import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import yaml


def _as_name_list(values: Iterable[str], what: str) -> list[str]:
    """Return a collection of names as a list, rejecting a bare string.

    A str is itself an iterable of str, so without this check a single name
    such as "co2" would silently be split into ["c", "o", "2"].

    Args:
        values: Collection of names (list, tuple, set, dict keys, etc.).
        what: Description of the argument, used in the error message.

    Returns:
        list[str]: The names, in iteration order.

    Raises:
        TypeError: If values is a str.
    """
    if isinstance(values, str):
        raise TypeError(
            f"{what} must be a collection of names, not the string {values!r}"
        )
    return [str(value) for value in values]


@dataclass(frozen=True)
class DatasetDirname:
    """Directory DRS facets for an input4MIPs dataset.

    Follows the ESGF/input4MIPs directory layout standard:
    <root>/<activity_id>/<mip_era>/<target_mip>/<institution_id>/<source_id>/
    <realm>/<frequency>/<variable_id>/<grid_label>/<version>/

    Attributes:
        mip_era: MIP era identifier (e.g., 'CMIP7', 'CMIP6').
        target_mip: Target MIP experiment context (e.g., 'CMIP', 'ScenarioMIP').
        institution_id: Data producer institution (e.g., 'FZJ', 'CR', 'CEDS').
        source_id: Source release identifier (e.g., 'FZJ-CMIP-nitrogen-1-2').
        realm: Modeling realm (e.g., 'atmos', 'ocean', 'land').
        frequency: Temporal frequency (e.g., 'mon', 'yr', 'day', 'monC', 'fx').
        variable_id: Variable identifier (e.g., 'drynhx', 'co2', 'multiple').
        grid_label: Grid label (e.g., 'gn', 'gm', 'gnz', 'gr').
        version: Publication version stamp (e.g., 'v20251025').
        activity_id: Activity identifier (default: 'input4MIPs').
    """

    mip_era: str
    target_mip: str
    institution_id: str
    source_id: str
    realm: str
    frequency: str
    variable_id: str
    grid_label: str
    version: str
    activity_id: str | None = "input4MIPs"

    def to_path(self, include_activity: bool = True) -> Path:
        """Assemble and return the relative directory path.

        Args:
            include_activity: Whether to include activity_id in the path.

        Returns:
            Path: Relative filesystem path for the directory hierarchy.
        """
        parts: list[str] = []
        if include_activity and self.activity_id:
            parts.append(self.activity_id)
        parts.extend(
            [
                self.mip_era,
                self.target_mip,
                self.institution_id,
                self.source_id,
                self.realm,
                self.frequency,
                self.variable_id,
                self.grid_label,
                self.version,
            ]
        )
        return Path(*parts)


@dataclass(frozen=True)
class DatasetFilename:
    """Filename DRS facets for an input4MIPs dataset.

    Follows the ESGF/input4MIPs filename standard:
    <variable_id>_<activity_id>_<dataset_category>_<target_mip>_<source_id>_
    <grid_label>[_<time_range>].<extension>

    Attributes:
        variable_id: Variable identifier (e.g., 'drynhx', 'co2', 'multiple').
        dataset_category: Category (e.g., 'surfaceFluxes', 'emissions').
        target_mip: Target MIP experiment context (e.g., 'CMIP', 'ScenarioMIP').
        source_id: Source release identifier (e.g., 'FZJ-CMIP-nitrogen-1-2').
        grid_label: Grid label (e.g., 'gn', 'gm', 'gnz').
        time_range: Optional date range string (e.g., '185001-202312').
        activity_id: Activity identifier (default: 'input4MIPs').
        extension: File extension without dot (default: 'nc').
        hyphenate_variable: Whether the filename spells variable_id with
            hyphens in place of underscores (e.g. variable_id
            'BC_em_anthro' appears as 'BC-em-anthro' in the filename of
            the input4MIPs emissions datasets). The directory facet is
            unaffected. Default: False.
    """

    variable_id: str
    dataset_category: str
    target_mip: str
    source_id: str
    grid_label: str
    time_range: str | None = None
    activity_id: str = "input4MIPs"
    extension: str = "nc"
    hyphenate_variable: bool = False

    def to_path(self) -> Path:
        """Assemble and return the DRS-compliant filename.

        Returns:
            Path: Single-element Path representing the filename.
        """
        variable = (
            self.variable_id.replace("_", "-")
            if self.hyphenate_variable
            else self.variable_id
        )
        parts = [
            variable,
            self.activity_id,
            self.dataset_category,
            self.target_mip,
            self.source_id,
            self.grid_label,
        ]
        if self.time_range:
            parts.append(self.time_range)
        filename = f"{'_'.join(parts)}.{self.extension}"
        return Path(filename)


@dataclass(frozen=True)
class Dataset(os.PathLike):
    """Complete input4MIPs dataset combining root path and DRS facets.

    Attributes:
        root: Base mount directory Path (e.g., '/g/data/qv56/replicas').
        dirname: DatasetDirname instance with directory facets.
        filename: DatasetFilename instance with filename facets.
    """

    root: Path
    dirname: DatasetDirname
    filename: DatasetFilename

    def to_path(self) -> Path:
        """Assemble the complete filesystem path.

        Avoids duplicating activity_id if root already terminates with it.

        Returns:
            Path: Full filesystem path to the NetCDF file.
        """
        root_path = Path(self.root)
        include_activity = not (
            self.dirname.activity_id
            and (
                root_path.name == self.dirname.activity_id
                or root_path.name.lower()
                == str(self.dirname.activity_id).lower()
            )
        )
        dir_path = self.dirname.to_path(include_activity=include_activity)
        return root_path / dir_path / self.filename.to_path()

    def __fspath__(self) -> str:
        """Return the file system representation for os.PathLike."""
        return str(self.to_path())

    def __str__(self) -> str:
        """Return the string representation of the full path."""
        return str(self.to_path())

    def for_variable(self, variable_id: str) -> "Dataset":
        """Return a new Dataset updated for a specific variable or species.

        Args:
            variable_id: Target variable identifier (e.g., 'drynhx').

        Returns:
            Dataset: Updated immutable Dataset.
        """
        new_dirname = replace(self.dirname, variable_id=variable_id)
        new_filename = replace(self.filename, variable_id=variable_id)
        return Dataset(
            root=self.root, dirname=new_dirname, filename=new_filename
        )

    def for_time_range(self, time_range: str | None) -> "Dataset":
        """Return a new Dataset updated for a specific time range chunk.

        Args:
            time_range: Date range string (e.g., '185001-189912'), or None.

        Returns:
            Dataset: Updated immutable Dataset.
        """
        new_filename = replace(self.filename, time_range=time_range)
        return Dataset(
            root=self.root, dirname=self.dirname, filename=new_filename
        )

    def for_version(self, source_id: str, version: str) -> "Dataset":
        """Return a new Dataset updated for a source release and version stamp.

        Args:
            source_id: Model source identifier (e.g.,
                'FZJ-CMIP-nitrogen-1-2').
            version: Publication version stamp (e.g., 'v20251025').

        Returns:
            Dataset: Updated immutable Dataset.
        """
        new_dirname = replace(
            self.dirname, source_id=source_id, version=version
        )
        new_filename = replace(self.filename, source_id=source_id)
        return Dataset(
            root=self.root, dirname=new_dirname, filename=new_filename
        )

    def for_target_mip(self, target_mip: str) -> "Dataset":
        """Return a new Dataset updated for a target experiment MIP.

        Args:
            target_mip: Experiment MIP identifier (e.g., 'ScenarioMIP').

        Returns:
            Dataset: Updated immutable Dataset.
        """
        new_dirname = replace(self.dirname, target_mip=target_mip)
        new_filename = replace(self.filename, target_mip=target_mip)
        return Dataset(
            root=self.root, dirname=new_dirname, filename=new_filename
        )

    def for_variables(self, variables: Iterable[str]) -> dict[str, "Dataset"]:
        """Return a dictionary of Datasets keyed by variable_id.

        Args:
            variables: Sequence or iterable of variable identifiers.

        Returns:
            dict[str, Dataset]: Mapping of variable_id to updated Dataset.
        """
        return {
            var: self.for_variable(var)
            for var in _as_name_list(variables, "variables")
        }

    def for_time_ranges(self, time_ranges: Iterable[str]) -> list["Dataset"]:
        """Return an ordered list of Datasets for sequential time chunks.

        Args:
            time_ranges: Ordered sequence or iterable of time range strings.

        Returns:
            list[Dataset]: Ordered list of updated Datasets.
        """
        return [
            self.for_time_range(tr)
            for tr in _as_name_list(time_ranges, "time_ranges")
        ]

    @classmethod
    def from_facets(
        cls,
        root: str | Path,
        mip_era: str,
        target_mip: str,
        institution_id: str,
        source_id: str,
        realm: str,
        frequency: str,
        variable_id: str,
        grid_label: str,
        version: str,
        dataset_category: str,
        time_range: str | None = None,
        activity_id: str = "input4MIPs",
        extension: str = "nc",
        hyphenate_variable: bool = False,
    ) -> "Dataset":
        """Construct a Dataset from unified DRS facets.

        Args:
            root: Base mount directory Path.
            mip_era: MIP era identifier (e.g., 'CMIP7').
            target_mip: Target MIP identifier (e.g., 'CMIP').
            institution_id: Institution identifier (e.g., 'FZJ').
            source_id: Source release identifier.
            realm: Realm identifier (e.g., 'atmos').
            frequency: Frequency identifier (e.g., 'mon').
            variable_id: Variable identifier (e.g., 'drynhx').
            grid_label: Grid label (e.g., 'gn').
            version: Version stamp (e.g., 'v20251025').
            dataset_category: Dataset category (e.g., 'surfaceFluxes').
            time_range: Optional date range string.
            activity_id: Activity identifier (default: 'input4MIPs').
            extension: File extension (default: 'nc').
            hyphenate_variable: Spell variable_id with hyphens in the
                filename (default: False).

        Returns:
            Dataset: Instantiated Dataset.
        """
        dirname = DatasetDirname(
            mip_era=mip_era,
            target_mip=target_mip,
            institution_id=institution_id,
            source_id=source_id,
            realm=realm,
            frequency=frequency,
            variable_id=variable_id,
            grid_label=grid_label,
            version=version,
            activity_id=activity_id,
        )
        filename = DatasetFilename(
            variable_id=variable_id,
            dataset_category=dataset_category,
            target_mip=target_mip,
            source_id=source_id,
            grid_label=grid_label,
            time_range=time_range,
            activity_id=activity_id,
            extension=extension,
            hyphenate_variable=hyphenate_variable,
        )
        return cls(root=Path(root), dirname=dirname, filename=filename)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Dataset":
        """Construct a Dataset from a dictionary.

        Supports both nested structure ('root', 'dirname', 'filename') and
        flat DRS facet dictionaries.

        Args:
            data: Mapping containing dataset metadata.

        Returns:
            Dataset: Instantiated Dataset.
        """
        data_dict = dict(data)
        if "dirname" in data_dict and "filename" in data_dict:
            root = Path(data_dict.get("root", "."))
            dirname_data = dict(data_dict["dirname"])
            filename_data = dict(data_dict["filename"])
            return cls(
                root=root,
                dirname=DatasetDirname(**dirname_data),
                filename=DatasetFilename(**filename_data),
            )

        root = Path(data_dict.pop("root", "."))
        activity_id = data_dict.pop("activity_id", "input4MIPs")
        dataset_category = data_dict.pop("dataset_category")
        time_range = data_dict.pop("time_range", None)
        extension = data_dict.pop("extension", "nc")
        hyphenate_variable = bool(data_dict.pop("hyphenate_variable", False))

        dirname = DatasetDirname(
            mip_era=data_dict["mip_era"],
            target_mip=data_dict["target_mip"],
            institution_id=data_dict["institution_id"],
            source_id=data_dict["source_id"],
            realm=data_dict["realm"],
            frequency=data_dict["frequency"],
            variable_id=data_dict["variable_id"],
            grid_label=data_dict["grid_label"],
            version=data_dict["version"],
            activity_id=activity_id,
        )
        filename = DatasetFilename(
            variable_id=data_dict["variable_id"],
            dataset_category=dataset_category,
            target_mip=data_dict["target_mip"],
            source_id=data_dict["source_id"],
            grid_label=data_dict["grid_label"],
            time_range=time_range,
            activity_id=activity_id,
            extension=extension,
            hyphenate_variable=hyphenate_variable,
        )
        return cls(root=root, dirname=dirname, filename=filename)


@dataclass
class DatasetConfig:
    """Configuration factory producing Datasets from YAML metadata.

    Attributes:
        root: Base mount directory Path.
        dirname_facets: Mapping of directory DRS facets.
        filename_facets: Mapping of filename DRS facets.
        variables: Sequence of variable identifiers for multi-species expansion.
        time_ranges: Sequence of time range strings for multi-chunk expansion.
    """

    root: Path
    dirname_facets: dict[str, Any]
    filename_facets: dict[str, Any]
    variables: list[str] = field(default_factory=list)
    time_ranges: list[str] = field(default_factory=list)

    DIRNAME_KEYS = {
        "mip_era",
        "target_mip",
        "institution_id",
        "source_id",
        "realm",
        "frequency",
        "variable_id",
        "grid_label",
        "version",
        "activity_id",
    }

    FILENAME_KEYS = {
        "variable_id",
        "dataset_category",
        "target_mip",
        "source_id",
        "grid_label",
        "time_range",
        "activity_id",
        "extension",
        "hyphenate_variable",
    }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DatasetConfig":
        """Create a DatasetConfig from a dictionary.

        Args:
            data: Raw dictionary loaded from configuration YAML.

        Returns:
            DatasetConfig: Instantiated configuration object.
        """
        data_dict = dict(data)
        root = Path(data_dict.pop("root", "."))
        variables = _as_name_list(data_dict.pop("variables", []), "variables")
        time_ranges = _as_name_list(
            data_dict.pop("time_ranges", []), "time_ranges"
        )

        if "variable_id" in data_dict and not variables:
            variables = [str(data_dict["variable_id"])]

        if "time_range" in data_dict and not time_ranges:
            if data_dict["time_range"] is not None:
                time_ranges = [str(data_dict["time_range"])]

        dirname_facets: dict[str, Any] = {}
        filename_facets: dict[str, Any] = {}

        if "dirname" in data_dict and isinstance(data_dict["dirname"], dict):
            dirname_facets.update(data_dict.pop("dirname"))

        if "filename" in data_dict and isinstance(data_dict["filename"], dict):
            filename_facets.update(data_dict.pop("filename"))

        for key, value in data_dict.items():
            if key in cls.DIRNAME_KEYS:
                dirname_facets[key] = value
            if key in cls.FILENAME_KEYS:
                filename_facets[key] = value

        dirname_facets.setdefault("mip_era", "CMIP7")
        dirname_facets.setdefault("activity_id", "input4MIPs")
        filename_facets.setdefault("activity_id", "input4MIPs")
        filename_facets.setdefault("extension", "nc")

        return cls(
            root=root,
            dirname_facets=dirname_facets,
            filename_facets=filename_facets,
            variables=variables,
            time_ranges=time_ranges,
        )

    @classmethod
    def from_yaml(
        cls,
        path: str | Path = "datasetconfig.yaml",
        section: str | None = None,
    ) -> "DatasetConfig":
        """Load configuration from a YAML file.

        Args:
            path: Filesystem path to the YAML file. Defaults to
                'datasetconfig.yaml'.
            section: Optional section name to load from a multi-section YAML
                file (e.g., scenario name 'h', 'ssp585').

        Returns:
            DatasetConfig: Instantiated configuration object.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the file contents cannot be parsed as a mapping.
            KeyError: If the requested section is not present in the YAML file.
        """
        yaml_path = Path(path)
        if not yaml_path.is_file():
            raise FileNotFoundError(
                f"Configuration file not found: {yaml_path}"
            )
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(
                f"YAML configuration at {yaml_path} must be a dictionary"
            )
        if section is not None:
            if section in data:
                return cls.from_dict(data[section])
            if "source_id" in data or "root" in data or "dirname" in data:
                return cls.from_dict(data)
            valid_keys = [k for k in data.keys() if not k.startswith("_")]
            raise KeyError(
                f"Section '{section}' not found in {yaml_path}. "
                f"Available sections: {valid_keys}"
            )
        return cls.from_dict(data)

    @classmethod
    def from_yaml_sections(
        cls, path: str | Path = "datasetconfig.yaml"
    ) -> dict[str, "DatasetConfig"]:
        """Load a multi-section YAML file into a dictionary of DatasetConfigs.

        Args:
            path: Filesystem path to the multi-section YAML file.

        Returns:
            dict[str, DatasetConfig]: Mapping of section name to DatasetConfig.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the file contents cannot be parsed as a mapping.
        """
        yaml_path = Path(path)
        if not yaml_path.is_file():
            raise FileNotFoundError(
                f"Configuration file not found: {yaml_path}"
            )
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(
                f"YAML configuration at {yaml_path} must be a dictionary"
            )
        return {sec: cls.from_dict(sec_data) for sec, sec_data in data.items()}

    def to_dataset(
        self,
        variable_id: str | None = None,
        time_range: str | None = None,
    ) -> Dataset:
        """Instantiate a single Dataset configured by this object.

        Args:
            variable_id: Optional variable identifier override.
            time_range: Optional time range string override.

        Returns:
            Dataset: Complete Dataset instance.

        Raises:
            ValueError: If variable_id cannot be determined.
        """
        var = (
            variable_id
            or self.dirname_facets.get("variable_id")
            or self.filename_facets.get("variable_id")
            or (self.variables[0] if self.variables else None)
        )
        if not var:
            raise ValueError(
                "variable_id must be specified in config or method call"
            )

        tr = (
            time_range
            or self.filename_facets.get("time_range")
            or (self.time_ranges[0] if self.time_ranges else None)
        )

        dir_facets = dict(self.dirname_facets)
        dir_facets["variable_id"] = var

        file_facets = dict(self.filename_facets)
        file_facets["variable_id"] = var
        file_facets["time_range"] = tr

        dirname = DatasetDirname(**dir_facets)
        filename = DatasetFilename(**file_facets)
        return Dataset(root=self.root, dirname=dirname, filename=filename)

    def to_datasets_by_variable(
        self, variables: Iterable[str] | None = None
    ) -> dict[str, Dataset]:
        """Produce a dictionary of Datasets keyed by variable_id.

        Args:
            variables: Optional variable identifiers. Defaults to
                self.variables.

        Returns:
            dict[str, Dataset]: Mapping of variable_id to Dataset.

        Raises:
            ValueError: If no variables are specified.
        """
        names = (
            self.variables
            if variables is None
            else _as_name_list(variables, "variables")
        )
        if not names:
            raise ValueError("No variables specified in config or method call")
        return {var: self.to_dataset(variable_id=var) for var in names}

    def check_variables(self, expected: Iterable[str]) -> None:
        """Check that the configured variables match the expected set.

        Generator scripts own the list of species they need (e.g. because
        molar masses or namelist layouts depend on it), while the YAML
        configuration lists the variables it provides. This check makes any
        disagreement between the two fail fast instead of being silently
        ignored.

        Args:
            expected: Variable identifiers required by the caller.

        Raises:
            ValueError: If variables are missing from, or unexpected in, the
                configuration.
        """
        expected_set = set(_as_name_list(expected, "expected"))
        configured_set = set(self.variables)
        missing = sorted(expected_set - configured_set)
        unexpected = sorted(configured_set - expected_set)
        if missing or unexpected:
            raise ValueError(
                "Dataset configuration variables do not match the expected "
                f"species: missing {missing}, unexpected {unexpected}"
            )

    def to_dataset_sequence(
        self,
        time_ranges: Iterable[str] | None = None,
        variable_id: str | None = None,
    ) -> list[Dataset]:
        """Produce an ordered list of Datasets for sequential time chunks.

        Args:
            time_ranges: Optional time range strings. Defaults to
                self.time_ranges.
            variable_id: Optional variable identifier override, for
                configurations shared by several variables.

        Returns:
            list[Dataset]: Ordered list of Datasets.

        Raises:
            ValueError: If no time ranges are specified.
        """
        trs = (
            self.time_ranges
            if time_ranges is None
            else _as_name_list(time_ranges, "time_ranges")
        )
        if not trs:
            raise ValueError(
                "No time ranges specified in config or method call"
            )
        return [
            self.to_dataset(variable_id=variable_id, time_range=tr)
            for tr in trs
        ]
