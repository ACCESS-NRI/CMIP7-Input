# CMIP7-Input Documentation

Welcome to the technical documentation for [ACCESS-NRI/CMIP7-Input](https://github.com/ACCESS-NRI/cmip7-input), the ancillary generation and forcing interpolation workflow for [ACCESS-ESM1.6](https://github.com/ACCESS-NRI/access-esm1.6-configs).

---

## Overview

The `CMIP7-Input` suite automates the ingestion, regridding, temporal interpolation, formatting, and model configuration patching of CMIP7 [input4MIPs](https://esgf-node.llnl.gov/projects/input4mips/) datasets. Orchestrated by a unified [Cylc 8](https://cylc.github.io/) workflow, the system produces binary Unified Model (UM) ancillary files (`.anc`), ASCII boundary condition tables (`.dat`), and Fortran namelist patches (`&clmchfcg`, `&coupling`, `&RUN_Radiation`) required across historical, pre-industrial, emission-driven, and future projection climate experiments.

{% raw %}
```mermaid
flowchart TD
    %% Custom Styles for W3C PROV Semantics
    classDef inputStyle fill:#e1f5fe,stroke:#0288d1,stroke-width:1.5px,color:#01579b
    classDef activityStyle fill:#e8f5e9,stroke:#2e7d32,stroke-width:1.5px,color:#1b5e20
    classDef outputStyle fill:#fff3e0,stroke:#e65100,stroke-width:1.5px,color:#bf360c
    classDef agentStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1.5px,color:#4a148c
    classDef targetStyle fill:#ede7f6,stroke:#4527a0,stroke-width:2px,color:#311b92

    %% Top Level: Inputs and Agents
    subgraph S_TOP["1. Source Inputs and Orchestrating Agents"]
        direction LR
        subgraph S_IN["Input Entities (prov:Entity)"]
            direction TB
            E_Raw[("Primary input4MIPs NetCDF<br><code>/g/data/qv56/...</code>")]:::inputStyle
            E_Ref[("Reference Auxiliary Data<br><i>N96 qrparm.mask / CMIP6 DMS</i>")]:::inputStyle
        end

        subgraph Agents["Agents (prov:Agent)"]
            direction TB
            AgCylc{{"Cylc 8 Suite Scheduler"}}:::agentStyle
            AgPkg{{"esm1p6_ancil (Iris / Ants / Mule)"}}:::agentStyle
            AgUK{{"UKESM Upstream Pipelines"}}:::agentStyle
        end
    end

    %% Middle Level: Transformation Pipeline
    subgraph S_ACT["2. Transformation Pipeline (prov:Activity)"]
        direction TB
        A_Ingest["Ingest and Validate<br><i>variables, units, dimensions</i>"]:::activityStyle
        A_Combine["Select and Combine<br><i>sector sum, species and time slice</i>"]:::activityStyle
        A_Regrid["Regrid and Interpolate<br><i>N96 area-weighted, Jan 1 realignment</i>"]:::activityStyle
        A_Pack["Reformat and Encode<br><i>Mule binary / ASCII / namelists</i>"]:::activityStyle

        A_Ingest --> A_Combine --> A_Regrid --> A_Pack
    end

    %% Lower Middle Level: Output Entities
    subgraph S_OUT["3. Forcing Products (prov:Entity)"]
        direction TB
        E_Anc[("Binary Ancillaries (<code>.anc</code>)<br><i>Aerosols, Ozone, Nitrogen, CO2, AMIP</i>")]:::outputStyle
        E_Dat[("ASCII Forcing Tables (<code>.dat</code>)<br><i>Solar TSI, Volcanic SAOD</i>")]:::outputStyle
        E_Nml[("Fortran Namelist Patches<br><i>clmchfcg, coupling, RUN_Radiation</i>")]:::outputStyle
    end

    %% Bottom Level: Downstream Model Configuration
    subgraph S_DEPLOY["4. Downstream Model Configuration"]
        E_Model[["ACCESS-ESM1.6 Configs<br><code>ACCESS-NRI/access-esm1.6-configs</code>"]]:::targetStyle
    end

    %% Provenance Relationships (flowing Top -> Bottom)
    E_Raw -->|prov:used| A_Ingest
    E_Ref -->|prov:used| A_Regrid

    A_Pack -->|prov:wasGeneratedBy| E_Anc
    A_Pack -->|prov:wasGeneratedBy| E_Dat
    A_Pack -->|prov:wasGeneratedBy| E_Nml

    E_Anc -->|staged into| E_Model
    E_Dat -->|staged into| E_Model
    E_Nml -->|Git commit and push| E_Model

    %% Agent Associations
    AgPkg -.->|prov:wasAssociatedWith| A_Ingest
    AgPkg -.->|prov:wasAssociatedWith| A_Combine
    AgPkg -.->|prov:wasAssociatedWith| A_Regrid
    AgPkg -.->|prov:wasAssociatedWith| A_Pack
    AgUK -.->|prov:wasAssociatedWith| A_Regrid
    AgCylc -.->|orchestrates| S_ACT
```
{% endraw %}

---

## Documentation Structure

This documentation is organized into three complementary perspectives to support workflow developers, domain scientists focused on specific physical forcings, and model operators configuring experiments:

### 1. [Suite Orchestration & Configuration](configuration/suite_objects.md)

Central orchestration, environment variables, and parameterization governing the Cylc 8 workflow suite:

* **[Suite Configuration & Parameters Reference](configuration/suite_objects.md):** A reference classifying suite configuration objects defined in `rose-suite.conf` and `site/nci-gadi/variables.cylc`. It documents master forcing switches (`ANCIL_CREATE_*`), experiment and scenario selectors (`USE_EXP`, `USE_SCEN`), timeline extension controls (`EXTEND_SM_*`), supercomputing site filesystem roots, input4MIPs dataset versions, target filenames, and downstream Git branch synchronization rules.

### 2. [Forcing Specifications](forcings/overview.md)

Detailed 9-dimension technical specifications for all workflow tasks, grouped by physical forcing domain and sub-grouped by experiment:

* **[Greenhouse Gases (GHG)](forcings/ghg.md):** Annual global-mean surface concentrations and `&clmchfcg` namelist patching.
* **[Aerosol Emissions](forcings/aerosols.md):** Anthropogenic surface, aircraft, biomass burning, and background DMS emissions (`BC`, `Bio`, `OC`, `SO2`).
* **[Carbon Dioxide Fluxes](forcings/co2.md):** Spatially distributed monthly surface CO2 emissions for carbon-cycle experiments.
* **[Nitrogen Deposition](forcings/nitrogen.md):** Reactive nitrogen deposition ancillaries (`Ndep`).
* **[Ozone Pipeline](forcings/ozone.md):** Multi-stage UKESM1 zonal-mean regridding and UM ozone ancillary generation.
* **[Solar Irradiance](forcings/solar.md):** Total Solar Irradiance (TSI) constant and annual timeseries (`TSI_CMIP7_ESM`).
* **[Volcanic Optical Depth](forcings/volcanic.md):** Stratospheric aerosol optical depth (SAOD) constants and timeseries (`volcts_cmip7.dat`).
* **[AMIP (SST & Sea Ice)](forcings/amip.md):** UKESM-derived sea surface temperature and sea-ice concentration ancillaries.
* **[Configuration Git Synchronization](forcings/config_sync.md):** Automated cloning, branching, namelist injection, and git synchronisation for `access-esm1.6-configs`.

### 3. [Experiments](experiments/overview.md)

Comprehensive pages covering experiment naming conventions, task execution flows, and configuration parameters for each supported climate experiment:

* **[Naming & Configuration Alignment](experiments/naming_alignment.md):** Bidirectional mapping between `CMIP7-Input` workflow acronyms and `access-esm1.6-configs` branch names.
* **[Pre-Industrial Control (PI)](experiments/pre_industrial.md):** Perpetual 1850 climatological forcing suite (12 tasks).
* **[Historical (HI)](experiments/historical.md):** Time-evolving 1850–2023 historical transient forcing suite (12 tasks).
* **[ScenarioMIP (SM)](experiments/scenariomip.md):** Future projections across pathways `h`, `hl`, `m`, and `vl`, supporting both standard (to 2100) and extended (to 2150) timelines (46 tasks).
* **[AMIP (AM)](experiments/amip.md):** Prescribed sea surface temperature and sea-ice boundary conditions (7 tasks).
* **[Emission-Driven Experiments (EH & ES)](experiments/emission_driven.md):** Carbon-cycle interactive CO2 emission experiments (5 tasks).
* **[Paleoclimate / PMIP (PM)](experiments/pmip.md):** Equilibrium paleoclimate ozone boundary conditions.

### 4. [Python API Reference](api/index.md)

Automated function-level API documentation generated via Sphinx:

* **[Python API Reference](api/index.md):** Complete reference covering all 55 modules and 192 functions in the `esm1p6_ancil` package across common utilities and 8 physical forcing domains (`aerosol`, `amip`, `co2`, `ghg`, `nitrogen`, `ozone`, `solar`, `volcanic`).

---

## The 9 Technical Dimensions

Every task specification in this documentation provides exhaustive coverage across 9 technical dimensions:

1. **Description & Purpose:** Physical domain scope and role in the workflow.
2. **CLI Arguments Passed:** Complete command-line arguments and flags.
3. **Input4MIPs Versions & Temporal Coverage:** Dataset versions, `vdate` timestamps, and date ranges.
4. **Input4MIPs Directory Paths & Filenames:** Absolute source file paths and naming patterns.
5. **Python Scripts & Functions Called:** Entrypoint script and internal calling structure.
6. **Function-Level Cube Transformations & Constraints:** Input and created Iris cubes, coordinate bounds handling, and applied constraints (name, date, wavelength).
7. **Produced File Versions & Date Ranges:** Ancillary versioning, temporal coverage, and calendar alignment.
8. **Produced File Directory Paths & Filenames:** Destination paths and output filenames.
9. **Namelist Updates:** Target namelist file, namelist group, and modified variables (or `None` for binary `.anc` files).

---

## Licensing & Acknowledgments

* **Code License:** Apache License 2.0.
* **Input Data:** CMIP7 input4MIPs datasets distributed via the Earth System Grid Federation (ESGF) and hosted locally on NCI Gadi (`/g/data/qv56/replicas/input4MIPs/CMIP7/`).
* **Governance:** Developed and maintained by the [Australian Climate and Earth System Simulator National Research Infrastructure (ACCESS-NRI)](https://www.access-nri.org.au/).
