"""Configuration file for the Sphinx documentation builder."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("../..").absolute().as_posix()))

# -- Project information -----------------------------------------------------
project = "sfs-settings"
copyright = "2025, Josh Marshall"  # noqa: A001
author = "Josh Marshall"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",  # For Google/NumPy style docstrings
]

templates_path = ["_templates"]
exclude_patterns = ["tests"]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Napoleon settings for docstring formatting ------------------------------
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

source_suffix = {
    ".rst": "restructuredtext",
}
