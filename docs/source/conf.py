"""Configuration file for the Sphinx documentation builder."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal

from sphinx.ext.autodoc import between

import sfs_settings

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.ext.autodoc import _AutodocProcessDocstringListener

# -- Project information -----------------------------------------------------
project = "sfs-settings"
copyright = "2025, Josh Marshall"  # noqa: A001
author = "Josh Marshall"
version = sfs_settings.__version__
release = sfs_settings.__version__

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",  # For Google/NumPy style docstrings
    "sphinx.ext.autosummary",  # For generating summary tables
    "sphinx.ext.intersphinx",  # For linking to other documentation
    "sphinx.ext.coverage",  # For checking documentation coverage
    "sphinx.ext.todo",  # For marking todos in documentation
    "sphinx.ext.doctest",  # For testing code examples in documentation
    "sphinx_autodoc_typehints",  # For better type hint rendering
    "sphinx.ext.doctest",
    # "pytest_sphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["tests"]

# Add this to prevent duplicate warnings
add_module_names = False

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

# Configure autosummary
autosummary_generate = True
autosummary_imported_members = True

source_suffix = {
    ".rst": "restructuredtext",
}

# Configure intersphinx for linking to external libraries
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "keyring": ("https://keyring.readthedocs.io/en/latest/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "python-dotenv": ("https://saurabh-kumar.com/python-dotenv/", None),
}

# Autodoc configuration
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "special-members": "__init__, __call__",
    "show-inheritance": True,
    "imported-members": True,
}

# Sort members by source order instead of alphabetically
autodoc_member_order = "bysource"

# Include private members in documentation
autodoc_default_flags = ["private-members"]

# Better typehints display
autodoc_typehints = "description"
autodoc_typehints_format = "fully-qualified"

# Set up todo extension
todo_include_todos = True

# Don't show type hints in function signatures
python_use_unqualified_type_names = True


# The complex return type causes issue with mypy.
def setup(  # type: ignore[return]
    app: Sphinx,  # noqa: ARG001
) -> _AutodocProcessDocstringListener | None:
    """Create a custom between handler for modules."""

    def between_handler(
        app: Sphinx,
        what: Literal["module", "class", "exception", "function", "method", "attribute"],
        name: str,
        obj: Any,
        options: dict[str, bool],
        lines: list[str],
    ) -> (
        Callable[
            [
                Sphinx,
                Literal["module", "class", "exception", "function", "method", "attribute"],
                str,
                Any,
                dict[str, bool],
                list[str],
            ],
            None,
        ]
        | None
    ):
        if what == "module":
            return between("DOCSTRING_START", "DOCSTRING_END")(app, what, name, obj, options, lines)
        return None


def process_pseudo_variable(
    app: Sphinx,  # noqa: ARG001
    what: Literal["module", "class", "exception", "function", "method", "attribute"],
    name: str,
    obj: Any,  # noqa: ARG001
    options: dict[str, bool],  # noqa: ARG001
    lines: list[str],
) -> None:
    """Add special handling for PseudoVariable class."""
    if what == "class" and name == "sfs_settings.pseudo_variable.PseudoVariable":
        lines.extend(["", "Special Methods:", ""])
        lines.extend(
            [
                "- `__call__()` - Returns the actual value",
                "- `__eq__(other)` - Compares with another value",
                "- `__str__()` - String representation of the value",
                "- `__repr__()` - Repr representation of the value",
            ]
        )


pygments_style = "sphinx"
pygments_dark_style = "monokai"

# Set up code block defaults
highlight_language = "python3"
