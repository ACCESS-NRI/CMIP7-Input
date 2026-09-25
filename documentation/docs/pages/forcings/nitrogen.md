# Nitrogen Deposition Forcing Specifications

The Nitrogen deposition pipeline aggregates 4 atmospheric reactive nitrogen deposition flux species from CMIP7, converts units to $\text{g}\,\text{m}^{-2}\,\text{day}^{-1}$, regrids conservatively to the `global.N96` grid, and outputs binary Unified Model ancillary files (`.anc`) for the CABLE / CASA-CNP terrestrial biogeochemistry scheme in ACCESS-ESM1.6.

---

## Physical Domain & Scientific Scope

* **Species Aggregated (4 fluxes):**
  1. Dry deposition of reduced nitrogen (`drynhx`, $\text{NH}_x$)
  2. Dry deposition of oxidized nitrogen (`drynoy`, $\text{NO}_y$)
  3. Wet deposition of reduced nitrogen (`wetnhx`, $\text{NH}_x$)
  4. Wet deposition of oxidized nitrogen (`wetnoy`, $\text{NO}_y$)
* **Total Deposition Calculation:**
  $$\text{Flux}_{\text{total}} = \text{drynhx} + \text{drynoy} + \text{wetnhx} + \text{wetnoy}$$
* **Unit Conversion:**
  Converted from standard CMIP7 flux units ($\text{kg}\,\text{m}^{-2}\,\text{s}^{-1}$) to Unified Model land biogeochemistry units ($\text{g}\,\text{m}^{-2}\,\text{day}^{-1}$) via:
  $$\text{Flux} \left[\text{g}\,\text{m}^{-2}\,\text{day}^{-1}\right] = \text{Flux} \left[\text{kg}\,\text{m}^{-2}\,\text{s}^{-1}\right] \times 1000.0 \times 86400.0$$
* **Target STASH Item:** `m01s00i884` (NITROGEN DEPOSITION).
* **Grid & Interpolation:** Conservative area-weighted regridding (`AreaWeighted(mdtol=0.5)`) using `esm_grid_mask_cube(args)`, with missing data filled to 0.0.

---

## 1. Pre-Industrial Experiment (PI)

### `PI_ancil_nitrogen`

* **1. Description & Purpose:**  
  Generates cyclic 1850 monthly reactive nitrogen deposition ancillaries for the pre-industrial control run (`Ndep_1850_cmip7.anc`).
* **2. CLI Arguments Passed:**  
  ```bash
  python -m esm1p6_ancil.nitrogen.cmip7_PI_nitrogen_generate \
      --ancil-target-dirname <ANCIL_TARGET_PATH> \
      --cmip7-source-data-dirname "${CMIP7_SOURCE_PATH}" \
      --esm15-inputs-dirname <ESM15_INPUTS_PATH> \
      --esm-grid-rel-dirname "global.N96" \
      --esm15-grid-version "2020.05.19" \
      --dataset-version "FZJ-CMIP-nitrogen-1-2" \
      --dataset-vdate "v20251025" \
      --dataset-date-range "185001-185012" \
      --save-filename "Ndep_1850_cmip7.anc"
  ```
* **3. Input4MIPs Versions & Temporal Metadata:**  
    * **Dataset Version:** `FZJ-CMIP-nitrogen-1-2`
    * **Version Date (`vdate`):** `v20251025`
    * **Input Date Range:** `185001-185012` (12 monthly slices)
* **4. Input4MIPs Directory Path & Filenames:**  
    * **Directory Path:** `/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/FZJ/FZJ-CMIP-nitrogen-1-2/atmos/mon/{species}/gn/v20251025/`
    * **Filenames (4 species):** `{species}_input4MIPs_surfaceFluxes_CMIP_FZJ-CMIP-nitrogen-1-2_gn_185001-185012.nc`
* **5. Python Scripts & Functions:**  
    * **Main Script / Entrypoint:** `esm1p6_ancil.nitrogen.cmip7_PI_nitrogen_generate`
    * **Key Functions Called:** `load_cmip7_nitrogen`, `regrid_cmip7_nitrogen`, `save_cmip7_nitrogen`, `fix_coords`, `esm_grid_mask_cube`, `save_ancil`
    * **Shared Libraries:** `iris`, `mule`, `ants`, `numpy`
* **6. Function-Level Cube Transformations & Constraints:**  
    * **Input Cubes & Coordinates:** Four 3D NetCDF cubes loaded into an `iris.cube.CubeList` representing `drynhx`, `drynoy`, `wetnhx`, and `wetnoy` on monthly time points.
    * **Constraints Applied:** Name constraints corresponding to standard CF names for nitrogen fluxes; attributes equalized via `equalise_attributes(nitrogen_cubes)`.
    * **Coordinate Bounds & Manipulation:**
        * Cubes summed elementwise into a total flux cube.
        * Units converted from `kg m-2 s-1` to `g m-2 day-1` via `cube_tot.convert_units("g m-2 day-1")`.
        * Coordinates standardized via `fix_coords(args, cube)`.
        * Regridded to `global.N96` using `AreaWeighted(mdtol=0.5)` against `esm_grid_mask_cube(args)`.
        * Missing values masked and zeroed (`data.filled(0.0)`).
        * STASH attribute assigned: `m01s00i884`.
    * **Created / Output Cubes:** Formats final 3D cube `(time: 12, lat: 144, lon: 192)` passed to `save_ancil`.
* **7. Produced File Versions & Date Ranges:**  
    * **Temporal Coverage:** `185001-185012` (12 monthly slices)
    * **Calendar:** 365-day (NoLeap) calendar alignment
    * **STASH Code:** `m01s00i884`
* **8. Produced File Directory Paths & Filenames:**  
    * **Output Directory:** `/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/<ISO_DATE_TODAY>/modern/pre-industrial/atmosphere/nitrogen/global.N96/<ANCIL_TODAY>/`
    * **Output Filename:** `Ndep_1850_cmip7.anc`
* **9. Namelist File & Variable Updates:**  
  `None (Generates binary ancillary .anc file)`.

---

## 2. Historical Experiment (HI)

### `HI_ancil_nitrogen`

* **1. Description & Purpose:**  
  Ingests monthly transient nitrogen deposition fluxes from 1850 to 2022, pads timeline to span 1849–2023 for model spin-up/spin-down boundary compliance, regrids to N96, and produces `Ndep_1849_2023_cmip7.anc`.
* **2. CLI Arguments Passed:**  
  ```bash
  python -m esm1p6_ancil.nitrogen.cmip7_HI_nitrogen_generate \
      --ancil-target-dirname <ANCIL_TARGET_PATH> \
      --cmip7-source-data-dirname "${CMIP7_SOURCE_PATH}" \
      --esm15-inputs-dirname <ESM15_INPUTS_PATH> \
      --esm-grid-rel-dirname "global.N96" \
      --esm15-grid-version "2020.05.19" \
      --dataset-version "FZJ-CMIP-nitrogen-1-2" \
      --dataset-vdate "v20251025" \
      --dataset-date-range "185001-202212" \
      --save-filename "Ndep_1849_2023_cmip7.anc"
  ```
* **3. Input4MIPs Versions & Temporal Metadata:**  
    * **Dataset Version:** `FZJ-CMIP-nitrogen-1-2`, `v20251025`, Range: `185001-202212`.
    * **Processed Model Timeline:** `184901-202312` (175 years, 2100 monthly slices).
* **4. Input4MIPs Directory Path & Filenames:**  
    * **Path:** `/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/FZJ/FZJ-CMIP-nitrogen-1-2/atmos/mon/{species}/gn/v20251025/`
    * **Filenames:** `{species}_input4MIPs_surfaceFluxes_CMIP_FZJ-CMIP-nitrogen-1-2_gn_185001-202212.nc`
* **5. Python Scripts & Functions:** `esm1p6_ancil.nitrogen.cmip7_HI_nitrogen_generate`, `load_cmip7_nitrogen`, `regrid_cmip7_nitrogen`, `extend_years`, `save_cmip7_nitrogen`.
* **6. Cube Transformations:**
    * Aggregates 4 species, converts units to `g m-2 day-1`.
    * Prepends 1849 (repeating 1850) and appends 2023 (repeating 2022) via `extend_years` to satisfy UM padding requirements.
    * Regrids to N96 (`AreaWeighted(mdtol=0.5)`) and sets STASH `m01s00i884`.
* **7. Produced File:** `Ndep_1849_2023_cmip7.anc` (2100 monthly slices, 1849–2023).
* **8. Destination Path:** `/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/.../modern/historical/atmosphere/nitrogen/global.N96/<DATE>/Ndep_1849_2023_cmip7.anc`.
* **9. Namelist Updates:** `None (Generates binary ancillary .anc file)`.

---

## 3. ScenarioMIP Experiment (SM)

### `SM_{h,hl,m,vl}_ancil_nitrogen`

=== "Scenario h (High)"
    * **1. Description & Purpose:** Generates future projection nitrogen deposition ancillaries for scenario `h`. When `--ext` is specified, extends 2022–2100 data to 2150 by tiling the final year (2100) or applying pathway extensions.
    * **2. CLI Arguments Passed:**
      ```bash
      python -m esm1p6_ancil.nitrogen.cmip7_SM_nitrogen_generate \
          --scenario h \
          --ancil-target-dirname <ANCIL_TARGET_PATH> \
          --cmip7-source-data-dirname "${CMIP7_SOURCE_PATH}" \
          --esm15-inputs-dirname <ESM15_INPUTS_PATH> \
          --esm-grid-rel-dirname "global.N96" \
          --esm15-grid-version "2020.05.19" \
          --dataset-version "FZJ-CMIP-nitrogen-h-1-0" \
          --dataset-vdate "v20260409" \
          --dataset-date-range "202201-210012" \
          --ext \
          --save-filename "Ndep_h_2022_2150_cmip7.anc"
      ```
    * **3. Input4MIPs Versions & Temporal Metadata:**  
        * Version: `FZJ-CMIP-nitrogen-h-1-0`, `v20260409`, Range: `202201-210012`.
        * Target Coverage: `2022-2150` (1548 monthly slices).
    * **4. Input4MIPs Directory Path & Filenames:**  
        * `/g/data/qv56/replicas/input4MIPs/CMIP7/ScenarioMIP/FZJ/FZJ-CMIP-nitrogen-h-1-0/atmos/mon/{species}/gn/v20260409/{species}_input4MIPs_surfaceFluxes_ScenarioMIP_FZJ-CMIP-nitrogen-h-1-0_gn_202201-210012.nc`
    * **5. Scripts & Functions:** `esm1p6_ancil.nitrogen.cmip7_SM_nitrogen_generate`, `load_cmip7_sm_nitrogen`, `regrid_cmip7_nitrogen`, `extend_years`, `save_cmip7_nitrogen`.
    * **6. Cube Transformations:** Aggregates 4 nitrogen species, converts units, extends time axis to 2150 via `extend_years`, regrids conservatively to N96, and attaches STASH item 884.
    * **7. Produced File:** `Ndep_h_2022_2150_cmip7.anc` (1548 monthly slices, 2022–2150).
    * **8. Destination Path:** `/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/.../modern/scen7-h/atmosphere/nitrogen/global.N96/<DATE>/Ndep_h_2022_2150_cmip7.anc`.
    * **9. Namelist Updates:** `None (Generates binary ancillary .anc file)`.

=== "Scenario hl (High-Low)"
    * Dataset: `FZJ-CMIP-nitrogen-hl-1-0`, `v20260706`, `202201-210012`.
    * Produces: `Ndep_hl_2022_2150_cmip7.anc` (STASH 884).

=== "Scenario m (Medium)"
    * Dataset: `FZJ-CMIP-nitrogen-m-1-0`, `v20260706`, `202201-210012`.
    * Produces: `Ndep_m_2022_2150_cmip7.anc` (STASH 884).

=== "Scenario vl (Very Low)"
    * Dataset: `FZJ-CMIP-nitrogen-vl-1-0`, `v20260409`, `202201-210012`.
    * Produces: `Ndep_vl_2022_2150_cmip7.anc` (STASH 884).
