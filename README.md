# CMIP7-Input: Code and documentation for ACCESS CMIP7 forcings and input files

This repository is intended for code and documentation related to the input data used by the ACCESS models used for CMIP7, notably [ACCESS-ESM1.6](https://github.com/ACCESS-NRI/access-esm1.6-configs) and [ACCESS-CM3](https://github.com/ACCESS-NRI/cm3-suite). This includes code and documentation related to transformations applied to [CMIP7 forcing files](https://wcrp-cmip.org/cmip7-task-teams/forcings/) to produce model input files for each CMIP7 experiment.

## Development strategies
NOTE: The following development strategies are suggestions, subject to discussion and confirmation

### Suggested code strategy

As much code as possible would be developed via this GitHub repository. The main exceptions would be the code and suites currently developed via [MOSRS](https://code.metoffice.gov.uk/) repositories such as [ANTS](https://code.metoffice.gov.uk/doc/ancil/ants/2.0/index.html), [the ANCIL Contrib project](https://code.metoffice.gov.uk/trac/ancil/browser/contrib/trunk/), Rose/Cylc suites, and Rose Stem tests. These would initially be developed via [contributing](https://code.metoffice.gov.uk/doc/ancil/ants/2.0/contributing.html) to the relevant MOSRS repository according to [current ANTS working practices](https://code.metoffice.gov.uk/trac/ancil/wiki/ANTS/WorkingPractices) and would be migrated to GitHub when appropriate. The GitHub Continuous Integration infrastructure for such MOSRS code would be developed in parallel with the code development via MOSRS.

### Suggested documentation strategy

Similarly, as much documentation as possible would be contained in the Wiki for this repository, then published to other locations when appropriate. The main exception would be documentation that describes some of the internal workings of some UK Met Office and Momentum Partnership projects, such as [the ANCIL project](https://code.metoffice.gov.uk/trac/ancil), [the UK CMIP6 project](https://code.metoffice.gov.uk/trac/ukcmip6), and [the UKESM project](https://code.metoffice.gov.uk/trac/UKESM).  In this case, only a top-level description would be given in the Wiki for this repository, with details in an appropriate MOSRS project Wiki.  

## Suggested project plan outline with major milestones

1. Document the correspondence between CMIP6 DECK forcings and ESM1.5 or ESM1.6 input files.
2. CMIP6 and CMIP7 DECK ancillary suite for ACCESS-ESM1.6, using updated Python scripts for ancillary generation.
3. CMIP7 DECK ancillary suite for ACCESS-*M3.
4. CMIP7 ancillary suite for CMIP7 MIPs for ACCESS-ESM1.6.
5. CMIP7 ancillary suite for CMIP7 MIPs for ACCESS-*M3.

Each of these milestones is to be broken down into goals, subgoals, and project items.

## Directory structure

* `attachments`

  Documents describing CMIP forcings that are not available elsewhere.

* `scripts`

  Scripts used to process CMIP forcings into model inputs.

* `scripts/mrd599/src/python`

  Python scripts selected from `gadi:/home/599/mrd599/src/python` and not contained in other repositories. These are scripts containing functions imported by some of the Python scripts in `scripts/txz599/ACCESS-ESM_tools`.

* `scripts/txz599/ACCESS-ESM_tools`

  Scripts selected from `gadi:/g/data/p66/txz599/ACCESS-ESM_tools` and not contained in other repositories. Some of these scripts were used in the processing of CMIP6 forcings into ESM1.5 inputs.

