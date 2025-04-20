"""noxfile.py."""

from __future__ import annotations

from pathlib import Path

import nox

# Configure nox to use Poetry for dependency management
nox.options.sessions = [
    "tests",
    "mypy",
    "lint",
    "coverage",
    "deduplicate_tests",
    "docs",
    "pre_commit",
    "setup_hooks",
    "security",
    "dependencies_scan",
    "dependencies_scan",
    "doctest",
    "doc_coverage",
    "doc_linkcheck",
]

# Check if we're running on NixOS
is_nixos = Path("/etc/nixos").exists()

versions = ["3.11", "3.12", "3.13"]


@nox.session(python=versions)
def tests(session: nox.Session) -> None:
    """Run the test suite with pytest."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "pytest", external=True)


@nox.session(python=versions[-1])
def mypy(session: nox.Session) -> None:
    """Run the static type checker."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "mypy", "sfs_settings", external=True)


@nox.session(python=versions[-1])
def lint(session: nox.Session) -> None:
    """Run the linter."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)

    # For NixOS, we need to use Python module directly instead of the binary
    if is_nixos:
        session.run("python", "-m", "ruff", "check", "sfs_settings", external=True)
        session.run("python", "-m", "ruff", "format", "--check", "sfs_settings", external=True)
    else:
        session.run("poetry", "run", "ruff", "check", "sfs_settings", external=True)
        session.run("poetry", "run", "ruff", "format", "--check", "sfs_settings", external=True)


@nox.session(python=versions[-1])
def security(session: nox.Session) -> None:
    """Run security checks."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)
    # For comprehensive security checks beyond what ruff offers
    session.run("poetry", "run", "bandit", "-r", "sfs_settings", external=True)


@nox.session(python=versions[-1])
def coverage(session: nox.Session) -> None:
    """Run the test suite and check code coverage."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)
    session.run(
        "poetry",
        "run",
        "pytest",
        "--cov=sfs_settings",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-branch",
        external=True,
    )


@nox.session(python=versions[-1])
def deduplicate_tests(session: nox.Session) -> None:
    """Run the test suite and check code coverage."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)
    session.run(
        "poetry",
        "run",
        "pytest_deduplicate",
        "--cov=sfs_settings",
        "--cov-branch",
        external=True,
    )


@nox.session(python=versions[-1])
def docs(session: nox.Session) -> None:
    """Build the documentation."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)

    # Create all required directories (but don't populate them)
    docs_paths = ["docs/source/_static", "docs/source/_templates"]

    for path in docs_paths:
        Path(path).mkdir(parents=True, exist_ok=True)

    # Just build the docs from the files in the repo
    session.run("poetry", "run", "sphinx-build", "-b", "html", "docs/source", "docs/build", external=True)


@nox.session(python=versions[-1])
def pre_commit(session: nox.Session) -> None:
    """Run all pre-commit hooks."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)  # Remove --extras dev
    session.run("poetry", "run", "pre-commit", "run", "--all-files", external=True)


@nox.session(python=versions[-1])
def setup_hooks(session: nox.Session) -> None:
    """Install pre-commit hooks."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "pre-commit", "install", external=True)


@nox.session(python=versions[-1])
def dependencies_scan(session: nox.Session) -> None:
    """Scan dependencies for security issues."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "safety", "scan", "--full-report", external=True)


@nox.session(python=versions[-1])
def doctest(session: nox.Session) -> None:
    """Run the doctest suite to ensure examples work."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)
    session.run(
        "poetry", "run", "sphinx-build", "-b", "doctest", "docs/source", "docs/build/doctest", external=True
    )


@nox.session(python=versions[-1])
def doc_coverage(session: nox.Session) -> None:
    """Check documentation coverage."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "coverage", "run", "--source=sfs_settings", "-m", "pytest", external=True)
    session.run(
        "poetry", "run", "sphinx-build", "-b", "coverage", "docs/source", "docs/build/coverage", external=True
    )
    session.run("poetry", "run", "cat", "docs/build/coverage/python.txt", external=True)


@nox.session(python=versions[-1])
def doc_linkcheck(session: nox.Session) -> None:
    """Check all internal and external links in the documentation."""
    session.run("poetry", "env", "use", session.python, external=True)
    session.run("poetry", "install", external=True)
    session.run(
        "poetry",
        "run",
        "sphinx-build",
        "-b",
        "linkcheck",
        "docs/source",
        "docs/build/linkcheck",
        external=True,
    )
