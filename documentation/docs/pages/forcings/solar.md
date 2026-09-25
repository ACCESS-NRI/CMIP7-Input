# Solar Irradiance (TSI) Forcing Specifications

The solar irradiance pipeline extracts and calculates Total Solar Irradiance (TSI) in $\text{W}\,\text{m}^{-2}$ from the SOLARIS-HEPPA CMIP7 datasets, patching the solar constant in model coupling namelists for pre-industrial experiments and manufacturing annual timeseries tables for historical and future projection simulations.

---

## Physical Domain & Scientific Scope

* **Physical Quantity:** Total Solar Irradiance ($S_0$, TSI) in $\text{W}\,\text{m}^{-2}$.
* **Source Dataset:** SOLARIS-HEPPA multi-variable solar forcing dataset (`multiple_input4MIPs_solar_...nc`).
* **Experiment Implementations:**
  * **Pre-Industrial Control (`PI`):** Constant scalar $S_0 = 1361.603\,\text{W}\,\text{m}^{-2}$ patched directly into namelist variable `SC` within group `&coupling` in `atmosphere/input_atm.nml`.
  * **Historical (`HI`):** Time-evolving annual mean values from 1850 to 2023 padded into an ASCII table `TSI_CMIP7_ESM` spanning 1700–2300 (years prior to 1850 filled with 1850 mean; years after 2023 set to missing data indicator `-32768.0`).
  * **ScenarioMIP (`SM`):** Future projection annual mean values from 2022 to 2299 padded into an ASCII table `TSI_CMIP7_ESM` spanning 1700–2300.

---

## 1. Pre-Industrial Experiment (PI)

### `PI_ancil_solar`

* **1. Description & Purpose:**  
  Extracts the pre-industrial solar constant from the time-invariant (`fx`) SOLARIS-HEPPA dataset and patches the `SC` variable in the `&coupling` namelist within the pre-industrial configuration branch.
* **2. CLI Arguments Passed:**  
  ```bash
  python -m esm1p6_ancil.solar.cmip7_PI_solar_generate \
      --ancil-target-dirname <ANCIL_TARGET_PATH> \
      --cmip7-source-data-dirname "${CMIP7_SOURCE_PATH}" \
      --esm15-inputs-dirname <ESM15_INPUTS_PATH> \
      --esm-grid-rel-dirname "global.N96" \
      --esm15-grid-version "2020.05.19" \
      --dataset-version "SOLARIS-HEPPA-CMIP-4-6" \
      --dataset-vdate "v20250219"
  ```
* **3. Input4MIPs Versions & Temporal Metadata:**  
  * **Dataset Version:** `SOLARIS-HEPPA-CMIP-4-6`
  * **Version Date (`vdate`):** `v20250219`
  * **Frequency:** `fx` (time-invariant)
* **4. Input4MIPs Directory Path & Filenames:**  
  * **Directory Path:** `/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/SOLARIS-HEPPA/SOLARIS-HEPPA-CMIP-4-6/atmos/fx/multiple/gn/v20250219/`
  * **Filename:** `multiple_input4MIPs_solar_CMIP_SOLARIS-HEPPA-CMIP-4-6_gn.nc`
* **5. Python Scripts & Functions:**  
  * **Main Script / Entrypoint:** `esm1p6_ancil.solar.cmip7_PI_solar_generate`
  * **Key Functions Called:** `load_cmip7_solar_cube`, `cmip7_solar_dirpath`, `cmip7_pi_solar_patch`, `f90nml.Parser`
  * **Shared Libraries:** `iris`, `f90nml`
* **6. Function-Level Cube Transformations & Constraints:**  
  * **Input Cubes:** Multi-field `fx` dataset loaded via `iris.load(path)`.
  * **Constraints Applied:** Name constraint `iris.Constraint(name="solar_irradiance")` extracts the TSI cube.
  * **Coordinate Bounds & Manipulation:** Scalar 1-point extraction at index `[0]`. No spatial regridding.
  * **Created / Output Value:** Scalar float `solar_irradiance = 1361.603` $\text{W}\,\text{m}^{-2}$ written to namelist `SC`.
* **7. Produced File Versions & Date Ranges:**  
  `None (Direct namelist generation)`. Time-invariant constant.
* **8. Produced File Directory Paths & Filenames:**  
  `None`.
* **9. Namelist File & Variable Updates:**  
  * **Target File:** `${GIT_PI_CONFIG_DIR}/atmosphere/input_atm.nml`
  * **Namelist Group:** `&coupling`
  * **Variable Updated:** `SC = 1361.603` (Format `.3f`)

---

## 2. Historical Experiment (HI)

### `HI_ancil_solar`

* **1. Description & Purpose:**  
  Ingests monthly historical solar irradiance fields (1850–2023), computes annual means, pads timeline from 1700 to 2300, and writes ASCII table file `TSI_CMIP7_ESM`.
* **2. CLI Arguments Passed:**  
  ```bash
  python -m esm1p6_ancil.solar.cmip7_HI_solar_generate \
      --ancil-target-dirname <ANCIL_TARGET_PATH> \
      --cmip7-source-data-dirname "${CMIP7_SOURCE_PATH}" \
      --esm15-inputs-dirname <ESM15_INPUTS_PATH> \
      --esm-grid-rel-dirname "global.N96" \
      --esm15-grid-version "2020.05.19" \
      --dataset-version "SOLARIS-HEPPA-CMIP-4-6" \
      --dataset-vdate "v20250219" \
      --dataset-date-range "185001-202312" \
      --pad \
      --save-filename "TSI_CMIP7_ESM"
  ```
* **3. Input4MIPs Versions & Temporal Metadata:**  
  * Version: `SOLARIS-HEPPA-CMIP-4-6`, `v20250219`, Date Range: `185001-202312`.
* **4. Input4MIPs Directory Path & Filenames:**  
  * `/g/data/qv56/replicas/input4MIPs/CMIP7/CMIP/SOLARIS-HEPPA/SOLARIS-HEPPA-CMIP-4-6/atmos/mon/multiple/gn/v20250219/multiple_input4MIPs_solar_CMIP_SOLARIS-HEPPA-CMIP-4-6_gn_185001-202312.nc`
* **5. Python Scripts & Functions:** `esm1p6_ancil.solar.cmip7_HI_solar_generate`, `load_cmip7_solar_cube`, `cmip7_solar_year_mean`, `cmip7_solar_save`.
* **6. Cube Transformations:** Extracts `solar_irradiance` cube, collapses monthly slices by year (`year_cube.collapsed("time", iris.analysis.MEAN)`), pads years 1700–1849 with 1850 value, and fills years 2024–2300 with `-32768.0`.
* **7. Produced File:** `TSI_CMIP7_ESM` (ASCII table, 601 rows for years 1700–2300).
* **8. Destination Path:** `/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/.../modern/historical/atmosphere/forcing/global.N96/<DATE>/TSI_CMIP7_ESM`.
* **9. Namelist Updates:** `None (Produces ASCII forcing table)`.

---

## 3. ScenarioMIP Experiment (SM)

### `SM_ancil_solar`

* **1. Description & Purpose:**  
  Generates projection solar irradiance table `TSI_CMIP7_ESM` for ScenarioMIP simulations spanning 2022 to 2299.
* **2. CLI Arguments Passed:**  
  ```bash
  python -m esm1p6_ancil.solar.cmip7_SM_solar_generate \
      --ancil-target-dirname <ANCIL_TARGET_PATH> \
      --cmip7-source-data-dirname "${CMIP7_SOURCE_PATH}" \
      --esm15-inputs-dirname <ESM15_INPUTS_PATH> \
      --esm-grid-rel-dirname "global.N96" \
      --esm15-grid-version "2020.05.19" \
      --dataset-version "SOLARIS-HEPPA-ScenarioMIP-4-6" \
      --dataset-vdate "v20260115" \
      --dataset-date-range "202201-229912" \
      --pad \
      --save-filename "TSI_CMIP7_ESM"
  ```
* **3. Input4MIPs Versions & Temporal Metadata:**  
  * Version: `SOLARIS-HEPPA-ScenarioMIP-4-6`, `v20260115`, Date Range: `202201-229912`.
* **7. Produced File:** `TSI_CMIP7_ESM` (ASCII table, 1700–2300).
* **8. Destination Path:** `/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/.../modern/scen7-h/atmosphere/forcing/global.N96/<DATE>/TSI_CMIP7_ESM`.
* **9. Namelist Updates:** `None (Produces ASCII forcing table)`.
