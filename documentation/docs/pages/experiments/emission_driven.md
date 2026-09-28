# Experiment Summary: Emission-Driven Experiments (EH & ES)

The Emission-Driven experiments evaluate Earth System feedbacks by driving ACCESS-ESM1.6 directly with anthropogenic surface and aircraft carbon dioxide emissions fluxes rather than prescribed atmospheric concentrations.

---

## Physical Forcing Rationale & Setup

* **Interactive Carbon Cycle:** Atmospheric CO2 concentrations are prognostic, rising and falling based on the balance between prescribed human emissions and simulated natural carbon uptake by land (CABLE/CASA-CNP) and ocean (WOMBAT).
* **Target STASH Item:** `m01s00i251` (SURFACE CO2 EMISSIONS FLUX).
* **Emissions Components Combined:** Total gridded surface emissions from energy, industrial, residential, transport, and agricultural sectors plus vertically integrated aircraft emissions.
* **Timeline Coverage:**
    * `EH`: 1849 to 2023 (including 1849 spin-up padding).
    * `ES`: 2022 to 2100 (standard) or 2022 to 2150 (extended).

---

## Workflow Switches & Selectors

The execution and extension of interactive CO2 emissions flux tasks are controlled by parameters in [`rose-suite.conf`](../configuration/suite_objects.md):

* **Master Forcing Toggle:** `ANCIL_CREATE_CO2 = true`  
  Must evaluate to `true` to schedule any carbon-cycle emissions flux tasks.
* **Experiment Activation Switches:**  
  * `USE_EXP['EH'] = True` schedules historical emissions interpolation (`EH_ancil_co2`).
  * `USE_EXP['ES'] = True` schedules ScenarioMIP emissions interpolation across active scenarios.
* **Scenario Pathway Selectors (`USE_SCEN`):**  
  Active future pathways are governed by `USE_SCEN['h']`, `USE_SCEN['hl']`, `USE_SCEN['m']`, and `USE_SCEN['vl']`.
* **2150 Extension Controls (`EXTEND_SM_CO2`):**  
  Controls whether future emissions pass `--ext` to concatenate 2150 extension datasets:
    * `'h': True` (Produces `${ESM_ES_EXT_CO2_SAVE_FILENAME['h']}` / `CO2_fluxes_h_2022_2150_cmip7.anc`)
    * `'hl': False` (Produces `${ESM_ES_CO2_SAVE_FILENAME['hl']}` / `CO2_fluxes_hl_2022_2100_cmip7.anc`)
    * `'m': False` (Produces `${ESM_ES_CO2_SAVE_FILENAME['m']}` / `CO2_fluxes_m_2022_2100_cmip7.anc`)
    * `'vl': True` (Produces `${ESM_ES_EXT_CO2_SAVE_FILENAME['vl']}` / `CO2_fluxes_vl_2022_2150_cmip7.anc`)
* **Reference:** See [Suite Configuration & Parameters Reference](../configuration/suite_objects.md) for full object declarations.

---

## Complete Task Roster for Emission-Driven Experiments

The following **5 Cylc workflow tasks** produce the required CO2 flux ancillary files:

| Task Name | Experiment | Script Entrypoint | Primary Input Datasets | Output Ancillary Filename | Technical Specification |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `EH_ancil_co2` | Emission Historical (`EH`) | `co2.cmip7_EH_CO2_interpolate` | `CEDS-CMIP-2025-04-18` (Surface + Air) | `${ESM_EH_CO2_SAVE_FILENAME}` (`CO2_fluxes_1849_2023_cmip7.anc`) | [View Card](../forcings/co2.md#1-emission-driven-historical-experiment-eh) |
| `ES_h_ancil_co2` | Emission ScenarioMIP High (`ES-h`) | `co2.cmip7_ES_CO2_interpolate` | `IIASA-IAMC-h-1-1-1` & `h-ext-1-1-1` | `${ESM_ES_EXT_CO2_SAVE_FILENAME['h']}` (`CO2_fluxes_h_2022_2150_cmip7.anc`) | [View Card](../forcings/co2.md#2-emission-driven-scenariomip-experiment-es) |
| `ES_hl_ancil_co2`| Emission ScenarioMIP High-Low (`ES-hl`)| `co2.cmip7_ES_CO2_interpolate` | `IIASA-IAMC-hl-1-1-1` | `${ESM_ES_CO2_SAVE_FILENAME['hl']}` (`CO2_fluxes_hl_2022_2100_cmip7.anc`) | [View Card](../forcings/co2.md#2-emission-driven-scenariomip-experiment-es) |
| `ES_m_ancil_co2` | Emission ScenarioMIP Medium (`ES-m`) | `co2.cmip7_ES_CO2_interpolate` | `IIASA-IAMC-m-1-1-1` | `${ESM_ES_CO2_SAVE_FILENAME['m']}` (`CO2_fluxes_m_2022_2100_cmip7.anc`) | [View Card](../forcings/co2.md#2-emission-driven-scenariomip-experiment-es) |
| `ES_vl_ancil_co2`| Emission ScenarioMIP Very Low (`ES-vl`)| `co2.cmip7_ES_CO2_interpolate` | `IIASA-IAMC-vl-1-1-1` & `vl-ext-1-1-1`| `${ESM_ES_EXT_CO2_SAVE_FILENAME['vl']}` (`CO2_fluxes_vl_2022_2150_cmip7.anc`) | [View Card](../forcings/co2.md#2-emission-driven-scenariomip-experiment-es) |

---

## Downstream Configuration Integration

Artifacts feed into the carbon-cycle configuration branches in `access-esm1.6-configs`:

* **Historical Emissions Branch (`esm-historical`):**  
  Files installed to `/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/<DATE>/modern/historical-emissions/atmosphere/forcing/global.N96/<DATE>/CO2_fluxes_1849_2023_cmip7.anc`.
* **ScenarioMIP Emissions Branches (`esm-scen7-<SCEN>`):**  
  Files installed to `/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/<DATE>/modern/esm-scen7-<SCEN>/atmosphere/forcing/global.N96/<DATE>/CO2_fluxes_<SCEN>_2022_2150_cmip7.anc`.
