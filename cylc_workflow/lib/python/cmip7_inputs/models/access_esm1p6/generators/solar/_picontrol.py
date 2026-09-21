"""Helpers for solar picontrol"""

from __future__ import annotations

from pathlib import Path
import f90nml

def patch_pi_solar(solar_irradiance):
    """
    Patch the SC variable in the coupling namelist
    """
    patch = {"coupling": {"SC": solar_irradiance}}
    patch_namelist = f90nml.namelist.Namelist(patch)
    # Set the floating point format to the right value
    patch_namelist.float_format = ".3f"
    # The floating point format is ignored unless
    # you print the namelist or convert it to a string
    patch_str = str(patch_namelist)
    parser = f90nml.Parser()
    patch_str_namelist = parser.reads(patch_str)

    # Create a new namelist by patching the original namelist
    pi_solar_namelist_filepath = Path("atmosphere") / "input_atm.nml"

    new_namelist_filepath = pi_solar_namelist_filepath.with_suffix(
        ".nml.patched"
    )
    parser.read(
        pi_solar_namelist_filepath, patch_str_namelist, new_namelist_filepath
    )

    # Replace the original namelist
    new_namelist_filepath.replace(pi_solar_namelist_filepath)