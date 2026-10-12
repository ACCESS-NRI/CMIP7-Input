# AMIP (SST & Sea Ice) Forcing Specifications

The AMIP (Atmospheric Model Intercomparison Project) forcing pipeline ingests observed sea surface temperature (SST) and sea-ice concentration fields from PCMDI to generate monthly boundary condition ancillary files (`.anc`) for prescribed-ocean experiments in ACCESS-ESM1.6.

---

## Physical Domain & Scientific Scope

* **Boundary Variables Generated:**
  1. **Sea Surface Temperature (`sst`):** Monthly mean sea surface skin temperature. Target STASH item: `m01s00i024` (SURFACE TEMPERATURE AFTER TIMESTEP).
  2. **Sea Ice Concentration (`seaice`):** Fractional area of grid cell covered by sea ice. Target STASH items: `m01s00i031` / `m01s00i032` (SEA ICE FRACTION).
* **Source Dataset:** PCMDI AMIP observational boundary dataset (`PCMDI-AMIP-1-1-10`, `v20250807`) spanning 1870 to 2022.
* **UKESM Intermediate Processing:**
  Utilizes the UK Met Office AMIP toolchain (`ancillary-file-science` on branch `1-port-cmip7-amip-code-for-esm16-site-nci`) to regrid PCMDI observations to the N96 atmospheric grid while applying area-preserving Taylor regridding and land-sea mask consistency adjustments.
* **Preservation of Ocean Cells:**
  Unlike land ancillaries which fill missing values with 0.0, AMIP ancillaries maintain strict ocean masks (`fill=False` in `fix_cmip7_ukesm`) to avoid corrupting coastal marine boundary temperatures.

---

## Provenance & Dataflow Architecture

The AMIP pipeline follows the W3C PROV framework, integrating upstream UKESM spatial regridding, Taylor temporal interpolation, and in-house Mule packaging with strict ocean mask preservation:

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
    subgraph S_TOP["1. Source Inputs and Agents"]
        direction LR
        subgraph Inputs["Input Entities (prov:Entity)"]
            direction TB
            E_TOS[("PCMDI tos (SST) NetCDF<br><code>PCMDI-AMIP-1-1-10 (1870-2022)</code>")]:::inputStyle
            E_SIC[("PCMDI siconc (Sea Ice) NetCDF<br><code>PCMDI-AMIP-1-1-10 (1870-2022)</code>")]:::inputStyle
            E_Mask[("Reference Grid Mask<br><code>qrparm.mask (N96)</code>")]:::inputStyle
        end

        subgraph Agents["Agents (prov:Agent)"]
            direction TB
            AgCylc{{"Cylc 8 Suite Scheduler"}}:::agentStyle
            AgUK{{"UKESM AMIP Scripts<br><i>cloned via git</i>"}}:::agentStyle
            AgPy{{"esm1p6_ancil.amip (Iris and Mule)"}}:::agentStyle
        end
    end

    %% Middle Level: Transformation Pipeline
    subgraph Activities["2. Multi-Stage Pipeline (prov:Activity)"]
        direction TB
        A_Regrid["Stage 1: UKESM Regridding<br><i>AM_ukesm_regrid (N96 spatial regrid)</i>"]:::activityStyle
        A_Taylor["Stage 2: Taylor Interpolation<br><i>AM_ukesm_taylor (daily -> monthly)</i>"]:::activityStyle
        A_Ancil["Stage 3: Intermediate Extraction<br><i>AM_ukesm_ancil</i>"]:::activityStyle
        A_Fix["Stage 4: Coordinate Alignment<br><i>fix_cmip7_ukesm (fill=False to preserve ocean mask)</i>"]:::activityStyle
        A_Mule["Stage 5: Mule Packaging<br><i>save_ancil (gregorian=False)</i>"]:::activityStyle

        A_Regrid --> A_Taylor --> A_Ancil --> A_Fix --> A_Mule
    end

    %% Lower Level: Output Entities
    subgraph Outputs["3. Output Entities (prov:Entity)"]
        direction TB
        E_TOS_Anc[("Time-Series SST Ancillary<br><code>tos.anc (STASH m01s00i024)</code>")]:::outputStyle
        E_SIC_Anc[("Time-Series Sea Ice Ancillary<br><code>siconc.anc (STASH m01s00i031)</code>")]:::outputStyle
    end

    %% Bottom Level: Model Target
    subgraph S_DEPLOY["4. Downstream Deployment"]
        E_Model[["ACCESS-ESM1.6 Configs<br><code>ACCESS-NRI/access-esm1.6-configs</code>"]]:::targetStyle
    end

    %% Relationships
    E_TOS & E_SIC -->|prov:used| A_Regrid
    E_Mask -->|prov:used| A_Fix
    A_Mule -->|prov:wasGeneratedBy| E_TOS_Anc & E_SIC_Anc

    E_TOS_Anc & E_SIC_Anc -->|staged for model execution| E_Model

    %% Agent Associations
    AgUK -.->|prov:wasAssociatedWith| A_Regrid
    AgUK -.->|prov:wasAssociatedWith| A_Taylor
    AgPy -.->|prov:wasAssociatedWith| A_Fix
    AgPy -.->|prov:wasAssociatedWith| A_Mule
    AgCylc -.->|orchestrates| Activities
```
{% endraw %}

---

## Controlling Suite Switches

The execution, experiment inclusion, and script branches for the AMIP pipeline are controlled by parameters in [`rose-suite.conf`](../configuration/suite_objects.md):

* **Master Activation Switch:** `ANCIL_CREATE_AMIP = true`  
  When set to `false`, all AMIP regridding and ancillary generation tasks are excluded from the Cylc task graph.
* **Experiment Activation:** Governed by `USE_EXP['AM'] = True`.
* **Variables Processed:** `AMIP_VARS = ['seaice', 'sst']`.
* **Upstream Scripts Branching:** Clones the AMIP regridding toolchain from `${GIT_ORG_URL}/${GIT_AMIP_SCRIPTS_REPO}.git` on branch `${GIT_AMIP_SCRIPTS_BRANCH}` (`1-port-cmip7-amip-code-for-esm16-site-nci`).
* **Reference:** See [Suite Configuration & Parameters Reference](../configuration/suite_objects.md) for full object declarations.

---

## 1. AMIP Infrastructure Tasks

### `git_clone_amip_scripts`
* **1. Description & Purpose:** Clones the AMIP processing repository from GitHub (`${GIT_ORG_URL}/${GIT_AMIP_SCRIPTS_REPO}` on branch `${GIT_AMIP_SCRIPTS_BRANCH}`) into `${CYLC_WORKFLOW_SHARE_DIR}/${GIT_AMIP_SCRIPTS_REPO}-amip`.
* **2. Execution:** `git clone --depth 1 -b ${GIT_AMIP_SCRIPTS_BRANCH} ${GIT_ORG_URL}/${GIT_AMIP_SCRIPTS_REPO}.git`.
* **7 & 8. Output:** Cloned directory in workflow share directory.

### `install_amip`
* **1. Description & Purpose:** Installs the cloned AMIP scripts and Python dependencies into the suite's environment.
* **2. Execution:** `pip install --no-deps -e ${CYLC_WORKFLOW_SHARE_DIR}/${GIT_AMIP_SCRIPTS_REPO}-amip`.

---

## 2. Upstream UKESM Regridding Tasks

### `AM_ukesm_regrid`
* **1. Description & Purpose:** Regrids raw monthly PCMDI SST and sea ice NetCDF files to the target N96 resolution using conservative interpolation.
* **3. Input4MIPs Version:** `${CMIP7_AMIP_VERSION}` (`PCMDI-AMIP-1-1-10`), `${CMIP7_AMIP_VDATE}` (`v20250807`), Range: `${CMIP7_AMIP_DATE_RANGE}` (`187001-202212`).
* **4. Input4MIPs Path:** `${VAR.CMIP7_SOURCE_PATH}/AMIP/PCMDI/${CMIP7_AMIP_VERSION}/ocean/mon/{var}/gn/${CMIP7_AMIP_VDATE}/`  
  *(Evaluated: `/g/data/qv56/replicas/input4MIPs/CMIP7/AMIP/PCMDI/PCMDI-AMIP-1-1-10/ocean/mon/{var}/gn/v20250807/`)*

### `AM_ukesm_taylor`
* **1. Description & Purpose:** Applies Taylor diagram verification and conservative flux-conserving smoothing to the regridded SST and sea-ice fields.

### `AM_ukesm_ancil`
* **1. Description & Purpose:** Packages the regridded fields into standardized UKESM intermediate NetCDF files: `${UKESM_AMIP_NETCDF_FILENAME['seaice']}` (`seaice_amip_n96_gregorian.nc`) and `${UKESM_AMIP_NETCDF_FILENAME['sst']}` (`sst_amip_n96_gregorian.nc`).

---

## 3. UM Binary Ancillary Generation Tasks

### `AM_seaice_ancil_amip`

* **1. Description & Purpose:** Reads the intermediate `${UKESM_AMIP_NETCDF_FILENAME['seaice']}` file, aligns coordinate definitions with the ACCESS-ESM1.6 N96 grid mask without zero-filling ocean points, and produces `${ESM_AMIP_SAVE_FILENAME['seaice']}` (`seaice_amip_n96_gregorian.anc`).
* **2. CLI Arguments Passed:**
  ```bash
  python -m esm1p6_ancil.amip.cmip7_AM_amip_generate \
      --ancil-target-dirname "${VAR.ANCIL_TARGET_PATH}" \
      # Current: "/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/$(isodatetime -f CCYY.MM.DD)"
      --cmip7-source-data-dirname "${VAR.CMIP7_SOURCE_PATH}" \
      # Current: "/g/data/qv56/replicas/input4MIPs/CMIP7"
      --esm15-inputs-dirname "${VAR.ESM15_INPUTS_PATH}" \
      # Current: "/g/data/vk83/configurations/inputs/access-esm1p5"
      --esm-grid-rel-dirname "${ESM_GRID_DIRNAME}" \
      # Current: "global.N96"
      --esm15-grid-version "${ESM15_GRID_VERSION}" \
      # Current: "2020.05.19"
      --ukesm-ancil-dirpath "${CYLC_WORKFLOW_SHARE_DIR}/" \
      --ukesm-netcdf-filename "${UKESM_AMIP_NETCDF_FILENAME['seaice']}" \
      # Current: "seaice_amip_n96_gregorian.nc"
      --save-filename "${ESM_AMIP_SAVE_FILENAME['seaice']}"
      # Current: "seaice_amip_n96_gregorian.anc"
  ```
* **5. Scripts & Functions:** `esm1p6_ancil.amip.cmip7_AM_amip_generate`, `load_cmip7_ukesm`, `fix_cmip7_ukesm`, `save_cmip7_am_amip`, `save_ancil`.
* **6. Cube Transformations:**
    * Loads 3D sea-ice cube `(time, lat, lon)` spanning 1870–2022.
    * Adjusts latitude and longitude coordinate metadata via `fix_cmip7_ukesm(args, ukesm_cube, fill=False)`.
    * Passes cube to `save_ancil` with `gregorian=False` to preserve standard 360-day or Proleptic Gregorian time headers.
* **7. Produced Ancillary:** `${ESM_AMIP_SAVE_FILENAME['seaice']}` (`seaice_amip_n96_gregorian.anc`, 1836 monthly slices, 1870–2022).
* **8. Destination Path:** `${VAR.ANCIL_TARGET_PATH}/modern/amip/atmosphere/boundary_conditions/${ESM_GRID_DIRNAME}/<DATE>/${ESM_AMIP_SAVE_FILENAME['seaice']}`.
* **9. Namelist Updates:** `None (Generates binary ancillary .anc file)`.

### `AM_sst_ancil_amip`

* **1. Description & Purpose:** Reads `${UKESM_AMIP_NETCDF_FILENAME['sst']}`, validates SST Kelvin units, aligns coordinates without zero-filling ocean cells, and produces `${ESM_AMIP_SAVE_FILENAME['sst']}` (`sst_amip_n96_gregorian.anc`).
* **2. CLI Arguments Passed:**
  ```bash
  python -m esm1p6_ancil.amip.cmip7_AM_amip_generate \
      --ancil-target-dirname "${VAR.ANCIL_TARGET_PATH}" \
      # Current: "/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/$(isodatetime -f CCYY.MM.DD)"
      --cmip7-source-data-dirname "${VAR.CMIP7_SOURCE_PATH}" \
      # Current: "/g/data/qv56/replicas/input4MIPs/CMIP7"
      --esm15-inputs-dirname "${VAR.ESM15_INPUTS_PATH}" \
      # Current: "/g/data/vk83/configurations/inputs/access-esm1p5"
      --esm-grid-rel-dirname "${ESM_GRID_DIRNAME}" \
      # Current: "global.N96"
      --esm15-grid-version "${ESM15_GRID_VERSION}" \
      # Current: "2020.05.19"
      --ukesm-ancil-dirpath "${CYLC_WORKFLOW_SHARE_DIR}/" \
      --ukesm-netcdf-filename "${UKESM_AMIP_NETCDF_FILENAME['sst']}" \
      # Current: "sst_amip_n96_gregorian.nc"
      --save-filename "${ESM_AMIP_SAVE_FILENAME['sst']}"
      # Current: "sst_amip_n96_gregorian.anc"
  ```
* **7. Produced Ancillary:** `${ESM_AMIP_SAVE_FILENAME['sst']}` (`sst_amip_n96_gregorian.anc`, 1836 monthly slices, 1870–2022).
* **8. Destination Path:** `${VAR.ANCIL_TARGET_PATH}/modern/amip/atmosphere/boundary_conditions/${ESM_GRID_DIRNAME}/<DATE>/${ESM_AMIP_SAVE_FILENAME['sst']}`.
* **9. Namelist Updates:** `None (Generates binary ancillary .anc file)`.
