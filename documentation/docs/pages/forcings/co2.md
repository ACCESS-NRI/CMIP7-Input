# Carbon Dioxide (CO2) Fluxes Forcing Specifications

The carbon dioxide flux pipeline processes monthly gridded anthropogenic surface and aircraft carbon dioxide emissions to produce Unified Model binary ancillary files (`.anc`) for emission-driven climate experiments in ACCESS-ESM1.6 (experiments `EH` and `ES`).

---

## Physical Domain & Scientific Scope

* **Scientific Purpose:** In standard concentration-driven simulations (`HI`, `SM`), atmospheric CO2 is prescribed via global-mean surface concentrations in `&clmchfcg`. In contrast, in emission-driven Earth System Model simulations (`EH`, `ES`), atmospheric CO2 evolves interactively through coupled carbon-cycle fluxes between the atmosphere, the CABLE land surface model, and the WOMBAT ocean biogeochemistry model, driven by prescribed spatially resolved emissions fluxes.
* **Target STASH Item:** `m01s00i251` (SURFACE CO2 EMISSIONS / CO2_FLUXES).
* **Grid & Interpolation:** Conservative area-weighted regridding (`AreaWeighted(mdtol=0.5)`) from $0.5^\circ$ native grid to `global.N96` ($1.875^\circ \times 1.25^\circ$), with polar boundary zeroing (`zero_poles`).
* **Source Components Combined:** Surface anthropogenic emissions (`CO2_em_anthro`, sum across economic sectors) plus 3D aircraft emissions collapsed vertically (`CO2_em_AIR_anthro`).

---

## 1. Emission-Driven Historical Experiment (EH)

### `EH_ancil_co2`

* **1. Description & Purpose:**  
  Generates historical gridded CO2 emissions fluxes spanning 1849 to 2023. Ingests anthropogenic surface emissions and aircraft emissions, sums sectors, regrids conservatively to N96, assigns STASH item 251, and saves `CO2_fluxes_1849_2023_cmip7.anc`.
* **2. CLI Arguments Passed:**  
  ```bash
  python -m esm1p6_ancil.co2.cmip7_EH_CO2_interpolate \
      --ancil-target-dirname <ANCIL_TARGET_PATH> \
      --cmip7-source-data-dirname "${CMIP7_SOURCE_PATH}" \
      --esm15-inputs-dirname <ESM15_INPUTS_PATH> \
      --esm-grid-rel-dirname "global.N96" \
      --esm15-grid-version "2020.05.19" \
      --dataset-version "CEDS-CMIP-2025-04-18" \
      --dataset-vdate "v20250421" \
      --dataset-date-range-list "['180001-184912','185001-189912','190001-194912','195001-199912','200001-202312']" \
      --save-filename "CO2_fluxes_1849_2023_cmip7.anc"
  ```
* **3. Input4MIPs Versions & Temporal Metadata:**  
    * **Dataset Version:** `CEDS-CMIP-2025-04-18`
    * **Version Date (`vdate`):** `v20250421`
    * **Input Date Range List:** `180001-184912`, `185001-189912`, `190001-194912`, `195001-199912`, `200001-202312`
    * **Processed Model Timeline:** `184901-202312` (2100 monthly slices)
* **4. Input4MIPs Directory Path & Filenames:**  
    * **Surface Path:** `/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/CEDS/CEDS-CMIP-2025-04-18/atmos/mon/CO2_em_anthro/gn/v20250421/`
    * **Aircraft Path:** `/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/CEDS/CEDS-CMIP-2025-04-18/atmos/mon/CO2_em_AIR_anthro/gn/v20250421/`
* **5. Python Scripts & Functions:**  
    * **Main Script / Entrypoint:** `esm1p6_ancil.co2.cmip7_EH_CO2_interpolate`
    * **Key Functions Called:** `cmip7_eh_co2_anthro_interpolate`, `load_cmip7_hi_aerosol_anthro`, `load_cmip7_hi_aerosol_air_anthro`, `esm_grid_mask_cube`, `zero_poles`, `save_ancil`
    * **Shared Libraries:** `iris`, `mule`, `ants`, `numpy`
* **6. Function-Level Cube Transformations & Constraints:**  
    * **Input Cubes & Coordinates:** Surface emissions cube `(time, sector, lat, lon)` and aircraft emissions cube `(time, altitude, lat, lon)`.
    * **Constraints Applied:** Date range constraint `cmip7_date_constraint_from_years(1849, 2023)` using `cftime.DatetimeNoLeap`.
    * **Coordinate Bounds & Manipulation:**
        * Surface sector coordinate collapsed via `cube.collapsed(["sector"], iris.analysis.SUM)` and removed via `remove_coord("sector")`.
        * Aircraft altitude coordinate collapsed via `cube_air.collapsed(["altitude"], iris.analysis.SUM)` and removed.
        * Combined total flux: `cube_tot = cube + cube_air`.
        * Regridded conservatively to target N96 grid using `AreaWeighted(mdtol=0.5)`. Missing values zeroed (`data.filled(0.0)`).
        * Polar singularity zeroed via `zero_poles(esm_cube)`.
        * Assigned STASH item `m01s00i251`.
    * **Created / Output Cubes:** Formats final 3D cube `(time: 2100, lat: 144, lon: 192)` passed to `save_ancil`.
* **7. Produced File Versions & Date Ranges:**  
    * **Temporal Coverage:** `184901-202312` (2100 monthly slices, including 1849 model spin-up padding)
    * **Calendar:** 365-day (NoLeap) calendar alignment
    * **STASH Code:** `m01s00i251`
* **8. Produced File Directory Paths & Filenames:**  
    * **Output Directory:** `/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/<ISO_DATE_TODAY>/modern/historical-emissions/atmosphere/forcing/global.N96/<ANCIL_TODAY>/`
    * **Output Filename:** `CO2_fluxes_1849_2023_cmip7.anc`
* **9. Namelist File & Variable Updates:**  
  `None (Generates binary ancillary .anc file)`.

---

## 2. Emission-Driven ScenarioMIP Experiment (ES)

### `ES_{h,hl,m,vl}_ancil_co2`

Tasks generate future projection CO2 emissions fluxes across scenarios `h`, `hl`, `m`, and `vl`, with automatic extension to 2150 when `--ext` is specified.

=== "Scenario h (High)"
    * **1. Description & Purpose:** Generates future surface CO2 emissions fluxes for ScenarioMIP scenario `h` (2022–2150). Combines surface and aircraft emissions, validates extension file availability via `check_aerosol_ext_available`, regrids conservatively to N96, and produces `CO2_fluxes_h_2022_2150_cmip7.anc`.
    * **2. CLI Arguments Passed:**
      ```bash
      python -m esm1p6_ancil.co2.cmip7_ES_CO2_interpolate \
          --scenario h \
          --ancil-target-dirname <ANCIL_TARGET_PATH> \
          --cmip7-source-data-dirname "${CMIP7_SOURCE_PATH}" \
          --esm15-inputs-dirname <ESM15_INPUTS_PATH> \
          --esm-grid-rel-dirname "global.N96" \
          --esm15-grid-version "2020.05.19" \
          --dataset-version "IIASA-IAMC-h-1-1-1" \
          --dataset-vdate "v20260409" \
          --dataset-date-range "202201-210012" \
          --dataset-air-version "IIASA-IAMC-h-1-1-2" \
          --dataset-air-vdate "v20260624" \
          --ext \
          --dataset-ext-version "IIASA-IAMC-h-ext-1-1-1" \
          --dataset-ext-vdate "v20260409" \
          --dataset-ext-date-range "210101-215012" \
          --dataset-air-ext-version "IIASA-IAMC-h-ext-1-1-2" \
          --dataset-air-ext-vdate "v20260804" \
          --dataset-air-ext-date-range "210501-250012" \
          --save-filename "CO2_fluxes_h_2022_2150_cmip7.anc"
      ```
    * **3. Input4MIPs Versions & Temporal Metadata:**
        * Surface Base: `IIASA-IAMC-h-1-1-1`, `v20260409`, `202201-210012`
        * Surface Ext: `IIASA-IAMC-h-ext-1-1-1`, `v20260409`, `210101-215012`
        * Aircraft Base: `IIASA-IAMC-h-1-1-2`, `v20260624`, `202201-210012`
        * Aircraft Ext: `IIASA-IAMC-h-ext-1-1-2`, `v20260804`, `210501-250012`
    * **4. Input4MIPs Directory Path & Filenames:**
        * Surface Base: `/g/data/qv56/replicas/input4MIPs/CMIP7/ScenarioMIP/IIASA-IAMC/IIASA-IAMC-h-1-1-1/atmos/mon/CO2_em_anthro/gn/v20260409/CO2-em-anthro_input4MIPs_emissions_ScenarioMIP_IIASA-IAMC-h-1-1-1_gn_202201-210012.nc`
        * Surface Ext: `/g/data/qv56/replicas/input4MIPs/CMIP7/ScenarioMIP/IIASA-IAMC/IIASA-IAMC-h-ext-1-1-1/atmos/mon/CO2_em_anthro/gn/v20260409/CO2-em-anthro_input4MIPs_emissions_ScenarioMIP_IIASA-IAMC-h-ext-1-1-1_gn_210101-215012.nc`
        * Aircraft Base: `/g/data/qv56/replicas/input4MIPs/CMIP7/ScenarioMIP/IIASA-IAMC/IIASA-IAMC-h-1-1-2/atmos/mon/CO2_em_AIR_anthro/gn/v20260624/CO2-em-AIR-anthro_input4MIPs_emissions_ScenarioMIP_IIASA-IAMC-h-1-1-2_gn_202201-210012.nc`
        * Aircraft Ext: `/g/data/qv56/replicas/input4MIPs/CMIP7/ScenarioMIP/IIASA-IAMC/IIASA-IAMC-h-ext-1-1-2/atmos/mon/CO2_em_AIR_anthro/gn/v20260804/CO2-em-AIR-anthro_input4MIPs_emissions_ScenarioMIP_IIASA-IAMC-h-ext-1-1-2_gn_210501-250012.nc`
    * **5. Scripts & Functions:** `esm1p6_ancil.co2.cmip7_ES_CO2_interpolate`, `cmip7_es_co2_anthro_interpolate`, `load_cmip7_sm_aerosol_anthro`, `load_cmip7_sm_aerosol_air_anthro`, `check_aerosol_ext_available`, `esm_grid_mask_cube`, `zero_poles`, `save_ancil`.
    * **6. Cube Transformations:**
        * Validates completeness of extension chunks via `check_aerosol_ext_available`.
        * Loads surface and aircraft cubes, collapses sectors and altitude coordinates.
        * Concatenates baseline (2022–2100) and extension (2101–2150) cubes.
        * Conservative regridding to N96 (`AreaWeighted(mdtol=0.5)`), zeroing polar edges, and assigning STASH `m01s00i251`.
    * **7. Produced File:** `CO2_fluxes_h_2022_2150_cmip7.anc` (1548 monthly slices, 2022–2150).
    * **8. Destination Path:** `/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/<ISO_DATE_TODAY>/modern/esm-scen7-h/atmosphere/forcing/global.N96/<ANCIL_TODAY>/CO2_fluxes_h_2022_2150_cmip7.anc`.
    * **9. Namelist Updates:** `None (Generates binary ancillary .anc file)`.

=== "Scenario hl (High-Low)"
    * Dataset Versions: Base `IIASA-IAMC-hl-1-1-1` (`v20260327`), Extension `IIASA-IAMC-hl-ext-1-1-1` (`v20260327`).
    * Produces: `CO2_fluxes_hl_2022_2150_cmip7.anc` (STASH 251).

=== "Scenario m (Medium)"
    * Dataset Versions: Base `IIASA-IAMC-m-1-1-1` (`v20260327`), Extension `IIASA-IAMC-m-ext-1-1-1` (`v20260327`).
    * Produces: `CO2_fluxes_m_2022_2150_cmip7.anc` (STASH 251).

=== "Scenario vl (Very Low)"
    * Dataset Versions: Base `IIASA-IAMC-vl-1-1-1` (`v20260409`), Extension `IIASA-IAMC-vl-ext-1-1-1` (`v20260409`).
    * Produces: `CO2_fluxes_vl_2022_2150_cmip7.anc` (STASH 251).
