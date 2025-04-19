# docs/source/generate_api_docs.py
"""Script to generate API documentation automatically."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path


def generate_api_docs(module_name: str, output_dir: str) -> None:
    """Generate API documentation for module."""
    module = importlib.import_module(module_name)
    output_path = Path(output_dir) / f"{module_name}.rst"

    with Path(output_path).open("w") as f:
        f.write(f"{module_name}\n")
        f.write("=" * len(module_name) + "\n\n")
        f.write(f".. automodule:: {module_name}\n")
        f.write("   :members:\n")
        f.write("   :undoc-members:\n")
        f.write("   :show-inheritance:\n\n")

        # Get all submodules
        for _name, obj in inspect.getmembers(module):
            if inspect.ismodule(obj) and obj.__name__.startswith(module_name):
                submodule_name = obj.__name__
                f.write(f"{submodule_name}\n")
                f.write("-" * len(submodule_name) + "\n\n")
                f.write(f".. automodule:: {submodule_name}\n")
                f.write("   :members:\n")
                f.write("   :undoc-members:\n")
                f.write("   :show-inheritance:\n\n")


if __name__ == "__main__":
    generate_api_docs("sfs_settings", "api")
