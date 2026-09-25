# Experiment Summary: Paleoclimate / PMIP (PM)

The Paleoclimate Modelling Intercomparison Project (`PMIP` or `PM`) investigates past climate states (e.g. Mid-Holocene, Last Glacial Maximum, Last Interglacial) to understand climate sensitivity and forced Earth System responses outside modern instrumental ranges.

---

## Physical Forcing Rationale & Setup

In paleoclimate simulations where astronomical orbital parameters and ice sheet geometries are modified, modern short-lived atmospheric chemistry must be replaced by a stable, multi-decadal equilibrium climatology:

* **20-Year Climatological Ozone Mean:** Rather than single-year 1850 fields which can exhibit transient anomalies, PMIP utilizes a 20-year climatological mean ozone field averaged over 1850–1870 (`ozone_1850_1870_mean_cmip7.anc`).
* **Vertical Structure:** Zonal-mean 85 hybrid-height levels (L85) on the standard `global.N96` atmospheric grid.

---

## Complete Task Roster for Paleoclimate

The following **2 Cylc workflow tasks** prepare the climatological ozone ancillary:

| Task Name | Pipeline Stage | Script Entrypoint | Primary Input Dataset | Output Artifact | Technical Specification |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `PI_mean_ukesm_ancil_ozone` | Upstream Regrid | UKESM ozone toolchain | `FZJ-CMIP-ozone-2-0` (1850–1870) | `mmro3_monthly_CMIP7_zonalmn_1850_1870_ants.nc` | [View Card](../forcings/ozone.md#pi_mean_ukesm_ancil_ozone-pi_mean_ancil_ozone) |
| `PI_mean_ancil_ozone` | UM Ancillary | `ozone.cmip7_PI_mean_ozone_generate` | Intermediate NetCDF | `ozone_1850_1870_mean_cmip7.anc` | [View Card](../forcings/ozone.md#pi_mean_ukesm_ancil_ozone-pi_mean_ancil_ozone) |

---

## Downstream Configuration Integration

Artifacts feed into the paleoclimate configuration branches in `access-esm1.6-configs`:

* **Installation Directory:**  
  `/g/data/${PROJECT}/${USER}/CMIP7/esm1p6_ancil/<ISO_DATE_TODAY>/modern/pre-industrial/atmosphere/forcing/global.N96/<ANCIL_TODAY>/`
* **Output Ancillary:** `ozone_1850_1870_mean_cmip7.anc` (12 monthly climatological slices).
