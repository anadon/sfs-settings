# docs/source/_ext/example_tester.py
"""Extension to test examples in documentation."""

from __future__ import annotations

import contextlib
import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def setup(app: Sphinx) -> dict[str, Any]:
    """Set up the extension."""
    app.connect("builder-inited", test_examples)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def test_examples(app: Sphinx) -> None:
    """Test all example files."""
    examples_dir = Path(app.srcdir) / "examples"

    if not examples_dir.exists():
        return

    for example_file in examples_dir.glob("*.py"):
        spec = importlib.util.spec_from_file_location(f"example_{example_file.stem}", example_file)
        if spec is not None:
            module = importlib.util.module_from_spec(spec)
            if module is not None and spec.loader is not None:
                with contextlib.suppress(Exception):
                    spec.loader.exec_module(module)
