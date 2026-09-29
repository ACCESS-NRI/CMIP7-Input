import sys
from pathlib import Path

# Insert package root to sys.path
PACKAGE_ROOT = (
    Path(__file__).resolve().parents[2]
    / "CMIP7"
    / "esm1p6"
    / "ancil"
    / "lib"
    / "python"
    / "esm1p6_ancil"
)
sys.path.insert(0, str(PACKAGE_ROOT))

project = "CMIP7-Input Python API"
copyright = "2025-2026 ACCESS-NRI"
author = "ACCESS-NRI"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_rtd_theme",
]

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "alphabetical",
}
autodoc_typehints = "description"

# Mock out heavy scientific and C-extension dependencies
autodoc_mock_imports = [
    "ants",
    "ants.io",
    "ants.io.save",
    "cf_units",
    "cftime",
    "f90nml",
    "iris",
    "iris.analysis",
    "iris.coord_categorisation",
    "iris.coords",
    "iris.cube",
    "iris.time",
    "iris.util",
    "mule",
    "mule.ancil",
    "netCDF4",
    "scipy",
    "scipy.interpolate",
]

# Napoleon settings for Google/NumPy docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "titles_only": False,
}
