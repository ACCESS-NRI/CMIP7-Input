Aerosol Emissions Pipeline
==========================

The aerosol emissions pipeline processes anthropogenic and biomass burning emissions across four species: Black Carbon (``BC``), Biomass (``Bio``), Organic Carbon (``OC``), and Sulfur Dioxide (``SO2``).

Function Summary
----------------

.. autosummary::
   :nosignatures:

   aerosol.cmip7_SM_aerosol_anthro._anthro_dirpath
   aerosol.cmip7_aerosol_anthro._anthro_dirpath
   aerosol.cmip7_SM_Bio_interpolate._biomass_dirpath
   aerosol.cmip7_aerosol_biomass._biomass_dirpath
   aerosol.cmip7_SM_Bio_interpolate._biomass_variable
   aerosol.cmip7_aerosol_anthro.cmip7_aerosol_air_anthro_filepath
   aerosol.cmip7_aerosol_anthro.cmip7_aerosol_anthro_filepath
   aerosol.cmip7_aerosol_anthro.cmip7_aerosol_anthro_interpolate
   aerosol.cmip7_aerosol_biomass.cmip7_aerosol_biomass_filepath
   aerosol.cmip7_aerosol_common.cmip7_aerosol_filepath_list
   aerosol.cmip7_HI_aerosol_anthro.cmip7_hi_aerosol_anthro_interpolate
   aerosol.cmip7_PI_aerosol_anthro.cmip7_pi_aerosol_anthro_interpolate
   aerosol.cmip7_SM_aerosol_anthro.cmip7_sm_aerosol_air_anthro_filepath
   aerosol.cmip7_SM_aerosol_anthro.cmip7_sm_aerosol_air_ext_anthro_filepath
   aerosol.cmip7_SM_aerosol_anthro.cmip7_sm_aerosol_anthro_filepath
   aerosol.cmip7_SM_aerosol_anthro.cmip7_sm_aerosol_anthro_interpolate
   aerosol.cmip7_SM_Bio_interpolate.cmip7_sm_aerosol_biomass_ext_filepath
   aerosol.cmip7_SM_Bio_interpolate.cmip7_sm_aerosol_biomass_filepath
   aerosol.cmip7_SM_aerosol_anthro.cmip7_sm_aerosol_ext_anthro_filepath
   aerosol.cmip7_HI_aerosol.esm_hi_aerosol_ancil_dirpath
   aerosol.cmip7_HI_aerosol.esm_hi_aerosol_save_dirpath
   aerosol.cmip7_PI_aerosol.esm_pi_aerosol_ancil_dirpath
   aerosol.cmip7_PI_aerosol.esm_pi_aerosol_save_dirpath
   aerosol.cmip7_SM_aerosol.esm_sm_aerosol_ancil_dirpath
   aerosol.cmip7_SM_aerosol.esm_sm_aerosol_save_dirpath
   aerosol.cmip7_aerosol_common.load_cmip7_aerosol
   aerosol.cmip7_aerosol_anthro.load_cmip7_aerosol_air_anthro_list
   aerosol.cmip7_aerosol_anthro.load_cmip7_aerosol_anthro
   aerosol.cmip7_aerosol_anthro.load_cmip7_aerosol_anthro_list
   aerosol.cmip7_SM_Bio_interpolate.load_cmip7_aerosol_biomass
   aerosol.cmip7_aerosol_biomass.load_cmip7_aerosol_biomass
   aerosol.cmip7_aerosol_biomass.load_cmip7_aerosol_biomass_list
   aerosol.cmip7_aerosol_common.load_cmip7_aerosol_list
   aerosol.cmip7_HI_aerosol_anthro.load_cmip7_hi_aerosol_air_anthro
   aerosol.cmip7_HI_aerosol_anthro.load_cmip7_hi_aerosol_anthro
   aerosol.cmip7_HI_Bio_interpolate.load_cmip7_hi_aerosol_biomass
   aerosol.cmip7_HI_Bio_interpolate.load_cmip7_hi_aerosol_biomass_percentage
   aerosol.cmip7_HI_SO2_interpolate.load_cmip7_hi_so2_aerosol_anthro
   aerosol.cmip7_PI_aerosol_anthro.load_cmip7_pi_aerosol_anthro
   aerosol.cmip7_PI_Bio_interpolate.load_cmip7_pi_aerosol_biomass
   aerosol.cmip7_PI_Bio_interpolate.load_cmip7_pi_aerosol_biomass_percentage
   aerosol.cmip7_SM_aerosol_anthro.load_cmip7_sm_aerosol_air_anthro
   aerosol.cmip7_SM_aerosol_anthro.load_cmip7_sm_aerosol_anthro
   aerosol.cmip7_SM_Bio_interpolate.load_cmip7_sm_aerosol_biomass
   aerosol.cmip7_SM_SO2_interpolate.load_cmip7_sm_so2_aerosol_anthro
   aerosol.cmip7_SO2_interpolate.load_dms
   aerosol.cmip7_HI_SO2_interpolate.load_hi_dms
   aerosol.cmip7_PI_SO2_interpolate.load_pi_dms
   aerosol.cmip7_SM_Bio_interpolate.load_sector_dict
   aerosol.cmip7_SO2_interpolate.load_sector_dict
   aerosol.cmip7_SM_SO2_interpolate.load_sm_dms
   aerosol.cmip7_HI_Bio_interpolate.parse_args
   aerosol.cmip7_HI_SO2_interpolate.parse_args
   aerosol.cmip7_HI_aerosol_anthro.parse_args
   aerosol.cmip7_PI_Bio_interpolate.parse_args
   aerosol.cmip7_PI_SO2_interpolate.parse_args
   aerosol.cmip7_PI_aerosol_anthro.parse_args
   aerosol.cmip7_SM_Bio_interpolate.parse_args
   aerosol.cmip7_SM_SO2_interpolate.parse_args
   aerosol.cmip7_SM_aerosol_anthro.parse_args
   aerosol.cmip7_aerosol_biomass.save_cmip7_aerosol_biomass
   aerosol.cmip7_SM_Bio_interpolate.save_cmip7_sm_aerosol_biomass
   aerosol.cmip7_SO2_interpolate.save_cmip7_so2_aerosol_anthro
   aerosol.cmip7_aerosol_biomass.split_frac_low_high
   aerosol.cmip7_SM_Bio_interpolate.split_sm_low_high
   aerosol.cmip7_SO2_interpolate.tile_yearly_data
   aerosol.cmip7_aerosol_common.zero_poles

Detailed Module Reference
-------------------------

cmip7_HI_BC_interpolate
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_HI_BC_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_HI_Bio_interpolate
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_HI_Bio_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_HI_OC_interpolate
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_HI_OC_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_HI_SO2_interpolate
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_HI_SO2_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_HI_aerosol
~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_HI_aerosol
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_HI_aerosol_anthro
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_HI_aerosol_anthro
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_PI_BC_interpolate
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_PI_BC_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_PI_Bio_interpolate
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_PI_Bio_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_PI_OC_interpolate
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_PI_OC_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_PI_SO2_interpolate
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_PI_SO2_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_PI_aerosol
~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_PI_aerosol
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_PI_aerosol_anthro
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_PI_aerosol_anthro
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_SM_BC_interpolate
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_SM_BC_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_SM_Bio_interpolate
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_SM_Bio_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_SM_OC_interpolate
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_SM_OC_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_SM_SO2_interpolate
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_SM_SO2_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_SM_aerosol
~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_SM_aerosol
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_SM_aerosol_anthro
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_SM_aerosol_anthro
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_SO2_interpolate
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_SO2_interpolate
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_aerosol_anthro
~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_aerosol_anthro
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_aerosol_biomass
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_aerosol_biomass
   :members:
   :undoc-members:
   :show-inheritance:

cmip7_aerosol_common
~~~~~~~~~~~~~~~~~~~~

.. automodule:: aerosol.cmip7_aerosol_common
   :members:
   :undoc-members:
   :show-inheritance:

